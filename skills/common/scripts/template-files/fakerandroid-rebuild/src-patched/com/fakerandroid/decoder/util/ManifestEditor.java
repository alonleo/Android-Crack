package com.fakerandroid.decoder.util;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.custommonkey.xmlunit.XMLConstants;
import org.dom4j.Attribute;
import org.dom4j.Document;
import org.dom4j.DocumentException;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;

/* JADX INFO: loaded from: ManifestEditor.class */
public class ManifestEditor {
    public static final String TAG_ACTIVITY = "activity";
    public static final String TAG_SERVICE = "service";
    public static final String TAG_PROVIDER = "provider";
    public static final String TAG_INTENT_FILTER = "intent-filter";
    File manifestFile;
    Document document;
    Element manifestElement;
    Element applicationElement;
    Element usessdk;

    public ManifestEditor(File manifestFile) throws DocumentException {
        this.manifestFile = manifestFile;
        SAXReader reader = new SAXReader();
        this.document = reader.read(manifestFile);
        this.manifestElement = this.document.getRootElement();
        this.applicationElement = this.manifestElement.element("application");
        this.usessdk = this.manifestElement.element("uses-sdk");
    }

    public Element getManifestElement() {
        return this.manifestElement;
    }

    public String getPackagenName() {
        return this.manifestElement.attributeValue("package");
    }

    public String getVersionName() {
        return this.manifestElement.attributeValue("versionName");
    }

    public String getVersionCode() {
        return this.manifestElement.attributeValue("versionCode");
    }

    public String getCompileSdkVersion() {
        return this.manifestElement.attributeValue("compileSdkVersion");
    }

    public String getPlatformBuildVersionCode() {
        return this.manifestElement.attributeValue("platformBuildVersionCode");
    }

    public String getMinSdkVersion() {
        if (this.usessdk != null) {
            return this.usessdk.attributeValue("minSdkVersion");
        }
        return null;
    }

    public String getTargetSdkVersion() {
        if (this.usessdk != null) {
            return this.usessdk.attributeValue("targetSdkVersion");
        }
        return null;
    }

    public String getNetConfig() {
        return this.applicationElement.attributeValue("networkSecurityConfig");
    }

    public void copyApplicaionElements(Element elementFrom, Element elementTo) {
        List<Element> elements = elementFrom.elements();
        for (Element element : elements) {
            if (!isMainActivityElement(element)) {
                Element copy = element.createCopy();
                elementTo.add(copy);
            }
        }
    }

    public Element getApplicationElement() {
        return this.applicationElement;
    }

    public String getAppName() {
        return this.applicationElement.attributeValue("label");
    }

    public String getApplicationName() {
        return this.applicationElement.attributeValue("name");
    }

    public String getAextractNativeLibs() {
        return this.applicationElement.attributeValue("extractNativeLibs");
    }

    public String getApplicationDebuggable() {
        return this.applicationElement.attributeValue("debuggable");
    }

    public List<String> getUsesPermissions() {
        List<String> permissions = new ArrayList<>();
        List<Element> permissionElements = this.manifestElement.elements("uses-permission");
        for (Element element : permissionElements) {
            permissions.add(element.attributeValue("name"));
        }
        return permissions;
    }

    public List<String> getPermissions() {
        List<String> permissions = new ArrayList<>();
        List<Element> permissionElements = this.manifestElement.elements("permission");
        for (Element element : permissionElements) {
            permissions.add(element.attributeValue("name"));
        }
        return permissions;
    }

    public String getLogoFileName() {
        String logoValue = this.applicationElement.attributeValue("icon");
        if (logoValue.contains(XMLConstants.XPATH_SEPARATOR)) {
            String logoFileName = logoValue.split(XMLConstants.XPATH_SEPARATOR)[1];
            return logoFileName;
        }
        return null;
    }

    public String getNetworkSecurityConfig() {
        String networkSecurityConfig = this.applicationElement.attributeValue("networkSecurityConfig");
        if (networkSecurityConfig == null) {
            return null;
        }
        return networkSecurityConfig.replace("@xml/", "");
    }

    public void modNetworkSecurityConfig(String name) {
        Attribute isSelfAttr = this.applicationElement.attribute("networkSecurityConfig");
        if (isSelfAttr != null) {
            isSelfAttr.setValue(String.format("@xml/%s", name));
        } else {
            this.applicationElement.addAttribute("android:networkSecurityConfig", String.format("@xml/%s", name));
        }
    }

    public Element getLancherActivityElement() {
        List<Element> activityElements = this.applicationElement.elements(TAG_ACTIVITY);
        for (Element activityElement : activityElements) {
            if (isMainActivityElement(activityElement)) {
                return activityElement;
            }
        }
        return null;
    }

    private boolean isProvider(Element element) {
        if (TAG_PROVIDER.equals(element.getName())) {
            return true;
        }
        return false;
    }

    private boolean isMainActivityElement(Element activityElement) {
        List<Element> filterElements = activityElement.elements(TAG_INTENT_FILTER);
        for (Element filterElement : filterElements) {
            List<Element> actionElements = filterElement.elements("action");
            boolean main = false;
            for (Element actionElement : actionElements) {
                if ("android.intent.action.MAIN".equals(actionElement.attributeValue("name"))) {
                    main = true;
                    break;
                }
            }
            boolean launcher = false;
            List<Element> categoryElements = filterElement.elements("category");
            for (Element categoryElement : categoryElements) {
                if ("android.intent.category.LAUNCHER".equals(categoryElement.attributeValue("name"))) {
                    launcher = true;
                    break;
                }
            }
            if (main && launcher) {
                return true;
            }
        }
        return false;
    }

    public List<String> getActivityNames() {
        List<String> strings = new ArrayList<>();
        List<Element> activityElements = this.applicationElement.elements(TAG_ACTIVITY);
        for (Element activityElement : activityElements) {
            String name = activityElement.attributeValue("name");
            strings.add(name);
        }
        return strings;
    }

    public String getLancherActivityName() {
        Element activityElement = getLancherActivityElement();
        if (activityElement == null) {
            return "";
        }
        String name = activityElement.attributeValue("name");
        if (name.startsWith(".")) {
            return getPackagenName() + name;
        }
        return name;
    }

    public void modModelProviderAuthorities(String domain, String replaceValue) {
        List<Element> providerElements = getProviderElements();
        for (Element element : providerElements) {
            if (isModelProvider(element, domain)) {
                String authorities = element.attributeValue("authorities");
                String authorities2 = authorities.replace(domain, replaceValue);
                Attribute isSelfAttr = element.attribute("authorities");
                isSelfAttr.setValue(authorities2);
            }
        }
    }

    public List<Element> getProviderElements() {
        return this.applicationElement.elements(TAG_PROVIDER);
    }

    boolean isModelProvider(Element element, String domain) {
        if (element.attributeValue("authorities").contains(domain)) {
            return true;
        }
        return false;
    }

    public void insertMeta(String metaKey, String metaValue) {
        if (checkIsExist(this.applicationElement, "meta-data", metaKey)) {
            throw new RuntimeException();
        }
        Element metaDataElement = this.applicationElement.addElement("meta-data");
        metaDataElement.addAttribute("android:name", metaKey);
        metaDataElement.addAttribute("android:value", metaValue);
    }

    public void coverMeta(String metaKey, String metaValue) {
        if (checkIsExist(this.applicationElement, "meta-data", metaKey)) {
            modMeta(metaKey, metaValue);
            return;
        }
        Element metaDataElement = this.applicationElement.addElement("meta-data");
        metaDataElement.addAttribute("android:name", metaKey);
        metaDataElement.addAttribute("android:value", metaValue);
    }

    public void modMeta(String name, String value) {
        List<Element> metaDataElements = this.applicationElement.elements("meta-data");
        for (Element element : metaDataElements) {
            String metaName = element.attributeValue("name");
            System.out.println("metaName------" + metaName);
            if (metaName.equals(name)) {
                element.attribute("value").setValue(value);
            }
        }
    }

    public void insertUsesPermission(String name) {
        if (checkIsExist(this.manifestElement, "uses-permission", name)) {
            return;
        }
        Element metaDataElement = this.manifestElement.addElement("uses-permission");
        metaDataElement.addAttribute("android:name", name);
    }

    public void insertPermission(String name, String protectLavel) {
        if (checkIsExist(this.manifestElement, "permission", name)) {
            return;
        }
        Element metaDataElement = this.manifestElement.addElement("permission");
        metaDataElement.addAttribute("android:name", name);
        if (!TextUtil.isEmpty(protectLavel)) {
            metaDataElement.addAttribute("android:protectionLevel", protectLavel);
        }
    }

    public void insertActivity(String name, String screenOrientation, String theme, String configChanges, String process) {
        if (checkIsExist(this.applicationElement, TAG_ACTIVITY, name)) {
            throw new RuntimeException();
        }
        Element activityElement = this.applicationElement.addElement(TAG_ACTIVITY);
        setActivityAttribute(name, screenOrientation, theme, configChanges, process, activityElement);
    }

    public void insertMainActivity(String name, String screenOrientation, String theme, String configChanges, String process) {
        if (checkIsExist(this.applicationElement, TAG_ACTIVITY, name)) {
            throw new RuntimeException();
        }
        Element activityElement = this.applicationElement.addElement(TAG_ACTIVITY);
        setActivityAttribute(name, screenOrientation, theme, configChanges, process, activityElement);
        Element intentFilter = activityElement.addElement(TAG_INTENT_FILTER);
        Element action = intentFilter.addElement("action");
        action.addAttribute("android:name", "android.intent.action.MAIN");
        Element category1 = intentFilter.addElement("category");
        category1.addAttribute("android:name", "android.intent.category.LAUNCHER");
    }

    public void insertActivityVivoWithFilter(String name, String screenOrientation, String theme, String configChanges, String proress) {
        if (checkIsExist(this.applicationElement, TAG_ACTIVITY, name)) {
            return;
        }
        Element activityElement = this.applicationElement.addElement(TAG_ACTIVITY);
        setActivityAttribute(name, screenOrientation, theme, configChanges, proress, activityElement);
        Element filter = activityElement.addElement(TAG_INTENT_FILTER);
        Element action = filter.addElement("action");
        action.addAttribute("android:name", "android.intent.action.VIEW");
        Element category1 = filter.addElement("category");
        category1.addAttribute("android:name", "android.intent.category.DEFAULT");
        Element category2 = filter.addElement("category");
        category2.addAttribute("android:name", "android.intent.category.BROWSABLE");
        Element data = filter.addElement("data");
        data.addAttribute("android:host", "union.vivo.com");
        data.addAttribute("android:path", "/openjump");
        data.addAttribute("android:scheme", "vivounion");
    }

    public void insertService(String name, String process, String priority, String exported) {
        if (checkIsExist(this.applicationElement, TAG_SERVICE, name)) {
            return;
        }
        Element serviceElement = this.applicationElement.addElement(TAG_SERVICE);
        serviceElement.addAttribute("android:name", name);
        if (!TextUtil.isEmpty(process)) {
            serviceElement.addAttribute("android:process", process);
        }
        if (!TextUtil.isEmpty(priority)) {
            serviceElement.addAttribute("android:priority", priority);
        }
        if (!TextUtil.isEmpty(exported)) {
            serviceElement.addAttribute("android:exported", exported);
        }
    }

    public void insertProvider(String name, String authorities, String exported, String grantUriPermissions, String metaName, String metaResource) {
        if (checkIsExist(this.applicationElement, TAG_PROVIDER, name)) {
            return;
        }
        Element provicerElement = this.applicationElement.addElement(TAG_PROVIDER);
        provicerElement.addAttribute("android:name", name);
        if (!TextUtil.isEmpty(authorities)) {
            provicerElement.addAttribute("android:authorities", authorities);
        }
        if (!TextUtil.isEmpty(exported)) {
            provicerElement.addAttribute("android:exported", exported);
        }
        if (!TextUtil.isEmpty(grantUriPermissions)) {
            provicerElement.addAttribute("android:grantUriPermissions", grantUriPermissions);
        }
        if (!TextUtil.isEmpty(metaName)) {
            Element meta = provicerElement.addElement("meta-data");
            meta.addAttribute("android:name", metaName);
            meta.addAttribute("android:resource", metaResource);
        }
    }

    private boolean checkIsExist(Element element, String tag, String name) {
        List<Element> originalElements = element.elements(tag);
        for (Element originalElement : originalElements) {
            String originalElementName = originalElement.attributeValue("name");
            if (name.equals(originalElementName)) {
                return true;
            }
        }
        return false;
    }

    public String getMateValue(String name) {
        List<Element> originalElements = this.applicationElement.elements("meta-data");
        for (Element originalElement : originalElements) {
            String originalElementName = originalElement.attributeValue("name");
            if (name.equals(originalElementName)) {
                return originalElement.attributeValue("value");
            }
        }
        return null;
    }

    public List<String> getMateNames() {
        List<Element> originalElements = this.applicationElement.elements("meta-data");
        List<String> metaNames = new ArrayList<>();
        for (Element originalElement : originalElements) {
            String originalElementName = originalElement.attributeValue("name");
            metaNames.add(originalElementName);
        }
        return metaNames;
    }

    private void setActivityAttribute(String name, String screenOrientation, String theme, String configChanges, String proress, Element activityElement) {
        activityElement.addAttribute("android:name", name);
        if (!TextUtil.isEmpty(screenOrientation)) {
            activityElement.addAttribute("android:screenOrientation", screenOrientation);
        }
        if (!TextUtil.isEmpty(theme)) {
            activityElement.addAttribute("android:theme", theme);
        }
        if (!TextUtil.isEmpty(configChanges)) {
            activityElement.addAttribute("android:configChanges", configChanges);
        }
        if (!TextUtil.isEmpty(proress)) {
            activityElement.addAttribute("android:process", proress);
        }
    }

    public void modApplication(String name) {
        String applicationName = getApplicationName();
        if (null == applicationName) {
            this.applicationElement.addAttribute("android:name", name);
        } else {
            Attribute isSelfAttr = this.applicationElement.attribute("name");
            isSelfAttr.setValue(name);
        }
    }

    public void extractNativeLibs() {
        String applicationName = getAextractNativeLibs();
        if (null == applicationName) {
            this.applicationElement.addAttribute("android:extractNativeLibs", "true");
        } else {
            Attribute isSelfAttr = this.applicationElement.attribute("extractNativeLibs");
            isSelfAttr.setValue("true");
        }
    }

    public void modApplicationTheme(String theme) {
        Attribute isSelfAttr = this.applicationElement.attribute("theme");
        if (isSelfAttr == null) {
            this.applicationElement.addAttribute("android:theme", theme);
        } else {
            isSelfAttr.setValue(theme);
        }
    }

    public void modPkg(String name) {
        Attribute isSelfAttr = this.manifestElement.attribute("package");
        isSelfAttr.setValue(name);
    }

    public void modApplicationLabel(String name) {
        Attribute isSelfAttr = this.applicationElement.attribute("label");
        isSelfAttr.setValue(name);
    }

    public void modLancherActivityLabel(String name) {
        Element lancherActivityElement = getLancherActivityElement();
        if (lancherActivityElement == null) {
            return;
        }
        Attribute isSelfAttr = lancherActivityElement.attribute("label");
        if (isSelfAttr == null) {
            lancherActivityElement.addAttribute("android:label", name);
        } else {
            isSelfAttr.setValue(name);
        }
    }

    public void modLancherActivityScreenOrientation(String screenOrientation) {
        Element lancherActivityElement = getLancherActivityElement();
        Attribute isSelfAttr = lancherActivityElement.attribute("screenOrientation");
        isSelfAttr.setValue(screenOrientation);
    }

    public void modLancherActivityTheme(String theme) {
        Element lancherActivityElement = getLancherActivityElement();
        Attribute isSelfAttr = lancherActivityElement.attribute("theme");
        if (isSelfAttr == null) {
            lancherActivityElement.addAttribute("android:theme", theme);
        } else {
            isSelfAttr.setValue(theme);
        }
    }

    public void modLancherActivityIntent() {
        Element lancherActivityElement = getLancherActivityElement();
        List<Element> intentFilters = lancherActivityElement.elements(TAG_INTENT_FILTER);
        for (Element ele : intentFilters) {
            lancherActivityElement.remove(ele);
        }
    }

    public static void main(String[] args) {
    }

    public void save() throws IOException {
        OutputFormat xmlFormat = OutputFormat.createPrettyPrint();
        xmlFormat.setEncoding("UTF-8");
        xmlFormat.setNewlines(true);
        xmlFormat.setIndent(true);
        xmlFormat.setIndent("    ");
        XMLWriter writer = new XMLWriter(new FileWriter(this.manifestFile), xmlFormat);
        writer.write(this.document);
        writer.close();
    }
}
