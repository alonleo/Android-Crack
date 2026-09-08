package com.fakerandroid.decoder;

import brut.androlib.ApkBuilder;
import brut.androlib.ApkDecoder;
import brut.androlib.ApktoolProperties;
import brut.androlib.Config;
import brut.androlib.exceptions.AndrolibException;
import brut.androlib.exceptions.CantFindFrameworkResException;
import brut.androlib.exceptions.InFileNotFoundException;
import brut.androlib.exceptions.OutDirExistsException;
import brut.androlib.res.Framework;
import brut.common.BrutException;
import brut.directory.ExtFile;
import brut.util.AaptManager;
import com.android.dx.rop.code.RegisterSpec;
import com.fakerandroid.decoder.api.Transfer;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import com.luhuiguo.chinese.ChineseUtils;
import com.luhuiguo.chinese.pinyin.PinyinFormat;
import java.io.File;
import java.io.IOException;
import java.util.logging.Formatter;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

/* JADX INFO: loaded from: Main.class */
public class Main {
    private static boolean advanceMode = false;
    private static final Options normalOptions = new Options();
    private static final Options BuildOptions = new Options();
    private static final Options DecodeOptions = new Options();
    private static final Options frameOptions = new Options();
    private static final Options allOptions = new Options();
    private static final Options emptyOptions = new Options();
    private static final Options emptyFrameworkOptions = new Options();

    /* JADX INFO: loaded from: Main$Verbosity.class */
    private enum Verbosity {
        NORMAL,
        VERBOSE,
        QUIET
    }

    public static void main(String[] args) throws BrutException, InterruptedException, IOException {
        System.setProperty("java.awt.headless", "true");
        Verbosity verbosity = Verbosity.NORMAL;
        CommandLineParser parser = new DefaultParser();
        _Options();
        try {
            CommandLine commandLine = parser.parse(allOptions, args, false);
            if (commandLine.hasOption("-v") || commandLine.hasOption("--verbose")) {
                verbosity = Verbosity.VERBOSE;
            } else if (commandLine.hasOption("-q") || commandLine.hasOption("--quiet")) {
                verbosity = Verbosity.QUIET;
            }
            setupLogging(verbosity);
            if (commandLine.hasOption("advance") || commandLine.hasOption("advanced")) {
                setAdvanceMode(true);
            }
            boolean cmdFound = false;
            for (String opt : commandLine.getArgs()) {
                if (opt.equalsIgnoreCase("fk") || opt.equalsIgnoreCase("fake")) {
                    cmdFakeProject(commandLine);
                    cmdFound = true;
                }
                if (opt.equalsIgnoreCase("d") || opt.equalsIgnoreCase("decode")) {
                    cmdDecode(commandLine);
                    cmdFound = true;
                } else if (opt.equalsIgnoreCase("b") || opt.equalsIgnoreCase("build")) {
                    cmdBuild(commandLine);
                    cmdFound = true;
                } else if (opt.equalsIgnoreCase("if") || opt.equalsIgnoreCase("install-framework")) {
                    cmdInstallFramework(commandLine);
                    cmdFound = true;
                } else if (opt.equalsIgnoreCase("empty-framework-dir")) {
                    cmdEmptyFrameworkDirectory(commandLine);
                    cmdFound = true;
                } else if (opt.equalsIgnoreCase("publicize-resources")) {
                    cmdPublicizeResources(commandLine);
                    cmdFound = true;
                }
            }
            if (!cmdFound) {
                if (commandLine.hasOption("version")) {
                    _version();
                    System.exit(0);
                } else {
                    usage();
                }
            }
        } catch (ParseException ex) {
            System.err.println(ex.getMessage());
            usage();
            System.exit(1);
        }
    }

    private static void cmdFakeProject(CommandLine cli) {
        int paraCount = cli.getArgList().size();
        String apkName = cli.getArgList().get(paraCount - 1);
        String outDir = null;
        if (cli.hasOption("o") || cli.hasOption("output")) {
            outDir = cli.getOptionValue("o");
        }
        if (outDir == null) {
            File originalFile = new File(apkName);
            File projectFile = new File(originalFile.getParent(), ChineseUtils.toPinyin(originalFile.getName().replace(".apk", ""), PinyinFormat.TONELESS_PINYIN_FORMAT).replace(" ", HelpFormatter.DEFAULT_OPT_PREFIX));
            outDir = projectFile.getAbsolutePath();
        }
        new Transfer(apkName, outDir, new TransformInvocation() { // from class: com.fakerandroid.decoder.Main.1
            @Override // com.fakerandroid.decoder.pipeline.TransformInvocation
            public void callBack(String msg) {
                Logger.getLogger(Transfer.class.getName()).info(msg);
            }
        }).translate();
    }

    private static void cmdDecode(CommandLine cli) throws AndrolibException {
        File outDir;
        int paraCount = cli.getArgList().size();
        String apkName = cli.getArgList().get(paraCount - 1);
        Config config = new Config();
        if (cli.hasOption("s") || cli.hasOption("no-src")) {
            config.mDecodeSources = 0;
        }
        if (cli.hasOption("only-main-classes")) {
            config.mDecodeSources = 16;
        }
        if (cli.hasOption("d") || cli.hasOption("debug")) {
            System.err.println("SmaliDebugging has been removed in 2.1.0 onward. Please see: https://github.com/iBotPeaches/Apktool/issues/1061");
            System.exit(1);
        }
        if (cli.hasOption("b") || cli.hasOption("no-debug-info")) {
            config.mBaksmaliDebugMode = false;
        }
        if (cli.hasOption("t") || cli.hasOption("frame-tag")) {
            config.mFrameworkTag = cli.getOptionValue("t");
        }
        if (cli.hasOption("f") || cli.hasOption("force")) {
            config.mForceDelete = true;
        }
        if (cli.hasOption("r") || cli.hasOption("no-res")) {
            config.mDecodeResources = 256;
        }
        if (cli.hasOption("force-manifest")) {
            config.mForceDecodeManifest = 1;
        }
        if (cli.hasOption("no-assets")) {
            config.mDecodeAssets = 0;
        }
        if (cli.hasOption("k") || cli.hasOption("keep-broken-res")) {
            config.mKeepBrokenResources = true;
        }
        if (cli.hasOption("p") || cli.hasOption("frame-path")) {
            config.mFrameworkDirectory = cli.getOptionValue("p");
        }
        if (cli.hasOption("m") || cli.hasOption("match-original")) {
            config.mAnalysisMode = true;
        }
        if (cli.hasOption("api") || cli.hasOption("api-level")) {
            config.mApiLevel = Integer.parseInt(cli.getOptionValue("api"));
        }
        if (cli.hasOption("o") || cli.hasOption("output")) {
            outDir = new File(cli.getOptionValue("o"));
        } else {
            String outName = apkName.endsWith(".apk") ? apkName.substring(0, apkName.length() - 4).trim() : apkName + ".out";
            outDir = new File(new File(outName).getName());
        }
        ApkDecoder decoder = new ApkDecoder(new ExtFile(apkName), config);
        try {
            decoder.decode(outDir);
        } catch (Throwable t) {
            if (t instanceof InFileNotFoundException) {
                System.err.println("Input file (" + apkName + ") was not found or was not readable.");
            } else if (t instanceof OutDirExistsException) {
                System.err.println("Destination directory (" + outDir.getAbsolutePath() + ") already exists. Use -f switch if you want to overwrite it.");
            } else if (t instanceof CantFindFrameworkResException) {
                System.err.println("Can't find framework resources for package of id: " + String.valueOf(((CantFindFrameworkResException) t).mPkgId) + ". You must install proper framework files, see project website for more info.");
            } else {
                System.err.println(t.getMessage());
            }
            System.exit(1);
        }
    }

    private static void cmdBuild(CommandLine cli) throws BrutException {
        File outFile;
        String[] args = cli.getArgs();
        String appDirName = args.length < 2 ? "." : args[1];
        Config config = new Config();
        if (cli.hasOption("f") || cli.hasOption("force-all")) {
            config.mForceBuildAll = true;
        }
        if (cli.hasOption("d") || cli.hasOption("debug")) {
            System.out.println("SmaliDebugging has been removed in 2.1.0 onward. Please see: https://github.com/iBotPeaches/Apktool/issues/1061");
            config.mDebugMode = true;
        }
        if (cli.hasOption(RegisterSpec.PREFIX) || cli.hasOption("verbose")) {
            config.mVerbose = true;
        }
        if (cli.hasOption("a") || cli.hasOption("aapt")) {
            config.mAaptBinary = new File(cli.getOptionValue("a"));
        }
        if (cli.hasOption("c") || cli.hasOption("copy-original")) {
            System.err.println("-c/--copy-original has been deprecated. Removal planned for v2.5.0 (#2129)");
            config.mCopyOriginalFiles = true;
        }
        if (cli.hasOption("p") || cli.hasOption("frame-path")) {
            config.mFrameworkDirectory = cli.getOptionValue("p");
        }
        if (cli.hasOption("nc") || cli.hasOption("no-crunch")) {
            config.mNoCrunch = true;
        }
        if (cli.hasOption("use-aapt2")) {
            config.mAaptVersion = 2;
        }
        if (cli.hasOption("api") || cli.hasOption("api-level")) {
            config.mApiLevel = Integer.parseInt(cli.getOptionValue("api"));
        }
        if (cli.hasOption("o") || cli.hasOption("output")) {
            outFile = new File(cli.getOptionValue("o"));
        } else {
            outFile = null;
        }
        try {
            if (cli.hasOption("a") || cli.hasOption("aapt")) {
                config.mAaptVersion = AaptManager.getAaptVersion(new File(cli.getOptionValue("a")));
            }
            new ApkBuilder(new ExtFile(appDirName), config).build(outFile);
        } catch (Throwable ex) {
            System.err.println(ex.getMessage());
            System.exit(1);
        }
    }

    private static void cmdInstallFramework(CommandLine cli) throws AndrolibException {
        int paraCount = cli.getArgList().size();
        String apkName = cli.getArgList().get(paraCount - 1);
        Config config = new Config();
        if (cli.hasOption("p") || cli.hasOption("frame-path")) {
            config.mFrameworkDirectory = cli.getOptionValue("p");
        }
        if (cli.hasOption("t") || cli.hasOption("tag")) {
            config.mFrameworkTag = cli.getOptionValue("t");
        }
        new Framework(config).install(new File(apkName));
    }

    private static void cmdPublicizeResources(CommandLine cli) throws AndrolibException {
        int paraCount = cli.getArgList().size();
        String apkName = cli.getArgList().get(paraCount - 1);
        new Framework(new Config()).publicizeResources(new File(apkName));
    }

    private static void cmdEmptyFrameworkDirectory(CommandLine cli) throws AndrolibException {
        Config config = new Config();
        if (cli.hasOption("f") || cli.hasOption("force")) {
            config.mForceDeleteFramework = true;
        }
        if (cli.hasOption("p") || cli.hasOption("frame-path")) {
            config.mFrameworkDirectory = cli.getOptionValue("p");
        }
        Framework framework = new Framework(config);
        File dir = framework.getDirectory();
        if (dir != null && dir.isDirectory()) {
            File[] files = dir.listFiles();
            if (files != null) {
                for (File f : files) {
                    f.delete();
                }
            }
        }
    }

    private static void _version() {
        System.out.println(ApktoolProperties.get("application.version"));
    }

    private static void _Options() {
        Option versionOption = Option.builder("version").longOpt("version").desc("prints the version then exits").build();
        Option advanceOption = Option.builder("advance").longOpt("advanced").desc("prints advance information.").build();
        Option noSrcOption = Option.builder("s").longOpt("no-src").desc("Do not decode sources.").build();
        Option onlyMainClassesOption = Option.builder().longOpt("only-main-classes").desc("Only disassemble the main dex classes (classes[0-9]*.dex) in the root.").build();
        Option noResOption = Option.builder("r").longOpt("no-res").desc("Do not decode resources.").build();
        Option forceManOption = Option.builder().longOpt("force-manifest").desc("Decode the APK's compiled manifest, even if decoding of resources is set to \"false\".").build();
        Option noAssetOption = Option.builder().longOpt("no-assets").desc("Do not decode assets.").build();
        Option debugDecOption = Option.builder("d").longOpt("debug").desc("REMOVED (DOES NOT WORK): Decode in debug mode.").build();
        Option analysisOption = Option.builder("m").longOpt("match-original").desc("Keeps files to closest to original as possible. Prevents rebuild.").build();
        Option apiLevelOption = Option.builder("api").longOpt("api-level").desc("The numeric api-level of the file to generate, e.g. 14 for ICS.").hasArg(true).argName("API").build();
        Option debugBuiOption = Option.builder("d").longOpt("debug").desc("Sets android:debuggable to \"true\" in the APK's compiled manifest").build();
        Option noDbgOption = Option.builder("b").longOpt("no-debug-info").desc("don't write out debug info (.local, .param, .line, etc.)").build();
        Option forceDecOption = Option.builder("f").longOpt("force").desc("Force delete destination directory.").build();
        Option frameTagOption = Option.builder("t").longOpt("frame-tag").desc("Uses framework files tagged by <tag>.").hasArg(true).argName("tag").build();
        Option frameDirOption = Option.builder("p").longOpt("frame-path").desc("Uses framework files located in <dir>.").hasArg(true).argName("dir").build();
        Option frameIfDirOption = Option.builder("p").longOpt("frame-path").desc("Stores framework files into <dir>.").hasArg(true).argName("dir").build();
        Option keepResOption = Option.builder("k").longOpt("keep-broken-res").desc("Use if there was an error and some resources were dropped, e.g.\n            \"Invalid config flags detected. Dropping resources\", but you\n            want to decode them anyway, even with errors. You will have to\n            fix them manually before building.").build();
        Option forceBuiOption = Option.builder("f").longOpt("force-all").desc("Skip changes detection and build all files.").build();
        Option aaptOption = Option.builder("a").longOpt("aapt").hasArg(true).argName("loc").desc("Loads aapt from specified location.").build();
        Option aapt2Option = Option.builder().longOpt("use-aapt2").desc("Upgrades apktool to use experimental aapt2 binary.").build();
        Option originalOption = Option.builder("c").longOpt("copy-original").desc("Copies original AndroidManifest.xml and META-INF. See project page for more info.").build();
        Option noCrunchOption = Option.builder("nc").longOpt("no-crunch").desc("Disable crunching of resource files during the build step.").build();
        Option tagOption = Option.builder("t").longOpt("tag").desc("Tag frameworks using <tag>.").hasArg(true).argName("tag").build();
        Option outputBuiOption = Option.builder("o").longOpt("output").desc("The name of apk that gets written. Default is dist/name.apk").hasArg(true).argName("dir").build();
        Option outputDecOption = Option.builder("o").longOpt("output").desc("The name of folder that gets written. Default is apk.out").hasArg(true).argName("dir").build();
        Option quietOption = Option.builder("q").longOpt("quiet").build();
        Option verboseOption = Option.builder(RegisterSpec.PREFIX).longOpt("verbose").build();
        if (isAdvanceMode()) {
            DecodeOptions.addOption(noDbgOption);
            DecodeOptions.addOption(keepResOption);
            DecodeOptions.addOption(analysisOption);
            DecodeOptions.addOption(onlyMainClassesOption);
            DecodeOptions.addOption(apiLevelOption);
            DecodeOptions.addOption(noAssetOption);
            DecodeOptions.addOption(forceManOption);
            BuildOptions.addOption(apiLevelOption);
            BuildOptions.addOption(debugBuiOption);
            BuildOptions.addOption(aaptOption);
            BuildOptions.addOption(originalOption);
            BuildOptions.addOption(aapt2Option);
            BuildOptions.addOption(noCrunchOption);
        }
        normalOptions.addOption(versionOption);
        normalOptions.addOption(advanceOption);
        DecodeOptions.addOption(frameTagOption);
        DecodeOptions.addOption(outputDecOption);
        DecodeOptions.addOption(frameDirOption);
        DecodeOptions.addOption(forceDecOption);
        DecodeOptions.addOption(noSrcOption);
        DecodeOptions.addOption(noResOption);
        BuildOptions.addOption(outputBuiOption);
        BuildOptions.addOption(frameDirOption);
        BuildOptions.addOption(forceBuiOption);
        frameOptions.addOption(tagOption);
        frameOptions.addOption(frameIfDirOption);
        emptyFrameworkOptions.addOption(forceDecOption);
        emptyFrameworkOptions.addOption(frameIfDirOption);
        for (Object op : normalOptions.getOptions()) {
            allOptions.addOption((Option) op);
        }
        for (Object op2 : DecodeOptions.getOptions()) {
            allOptions.addOption((Option) op2);
        }
        for (Object op3 : BuildOptions.getOptions()) {
            allOptions.addOption((Option) op3);
        }
        for (Object op4 : frameOptions.getOptions()) {
            allOptions.addOption((Option) op4);
        }
        allOptions.addOption(apiLevelOption);
        allOptions.addOption(analysisOption);
        allOptions.addOption(debugDecOption);
        allOptions.addOption(noDbgOption);
        allOptions.addOption(forceManOption);
        allOptions.addOption(noAssetOption);
        allOptions.addOption(keepResOption);
        allOptions.addOption(debugBuiOption);
        allOptions.addOption(aaptOption);
        allOptions.addOption(originalOption);
        allOptions.addOption(verboseOption);
        allOptions.addOption(quietOption);
        allOptions.addOption(aapt2Option);
        allOptions.addOption(noCrunchOption);
        allOptions.addOption(onlyMainClassesOption);
    }

    private static String verbosityHelp() {
        if (isAdvanceMode()) {
            return "[-q|--quiet OR -v|--verbose] ";
        }
        return "";
    }

    private static void usage() {
        _Options();
        HelpFormatter formatter = new HelpFormatter();
        formatter.setWidth(120);
        System.out.println("Apktool v" + ApktoolProperties.get("application.version") + " - a tool for reengineering Android apk files\nwith smali v2.5.2 and baksmali v2.5.2\nCopyright 2014 Ryszard Wi艣niewski <brut.alll@gmail.com>\nUpdated by Connor Tumbleson <connor.tumbleson@gmail.com>");
        if (isAdvanceMode()) {
            System.out.println("Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)\n");
        } else {
            System.out.println("");
        }
        formatter.printHelp("apktool " + verbosityHelp(), normalOptions);
        formatter.printHelp("apktool " + verbosityHelp() + "if|install-framework [options] <framework.apk>", frameOptions);
        formatter.printHelp("apktool " + verbosityHelp() + "d[ecode] [options] <file_apk>", DecodeOptions);
        formatter.printHelp("apktool " + verbosityHelp() + "b[uild] [options] <app_path>", BuildOptions);
        if (isAdvanceMode()) {
            formatter.printHelp("apktool " + verbosityHelp() + "publicize-resources <file_path>", emptyOptions);
            formatter.printHelp("apktool " + verbosityHelp() + "empty-framework-dir [options]", emptyFrameworkOptions);
            System.out.println("");
        } else {
            System.out.println("");
        }
        System.out.println("For additional info, see: http://ibotpeaches.github.io/Apktool/ \nFor smali/baksmali info, see: https://github.com/JesusFreke/smali");
    }

    private static void setupLogging(final Verbosity verbosity) {
        Logger logger = Logger.getLogger("");
        for (Handler handler : logger.getHandlers()) {
            logger.removeHandler(handler);
        }
        LogManager.getLogManager().reset();
        if (verbosity == Verbosity.QUIET) {
            return;
        }
        Handler handler2 = new Handler() { // from class: com.fakerandroid.decoder.Main.2
            @Override // java.util.logging.Handler
            public void publish(LogRecord record) {
                if (getFormatter() == null) {
                    setFormatter(new SimpleFormatter());
                }
                try {
                    String message = getFormatter().format(record);
                    if (record.getLevel().intValue() >= Level.WARNING.intValue()) {
                        System.err.write(message.getBytes());
                    } else if (record.getLevel().intValue() >= Level.INFO.intValue() || verbosity == Verbosity.VERBOSE) {
                        System.out.write(message.getBytes());
                    }
                } catch (Exception exception) {
                    reportError(null, exception, 5);
                }
            }

            @Override // java.util.logging.Handler
            public void close() throws SecurityException {
            }

            @Override // java.util.logging.Handler
            public void flush() {
            }
        };
        logger.addHandler(handler2);
        if (verbosity == Verbosity.VERBOSE) {
            handler2.setLevel(Level.ALL);
            logger.setLevel(Level.ALL);
        } else {
            handler2.setFormatter(new Formatter() { // from class: com.fakerandroid.decoder.Main.3
                @Override // java.util.logging.Formatter
                public String format(LogRecord record) {
                    return record.getLevel().toString().charAt(0) + ": " + record.getMessage() + System.getProperty("line.separator");
                }
            });
        }
    }

    private static boolean isAdvanceMode() {
        return advanceMode;
    }

    private static void setAdvanceMode(boolean advanceMode2) {
        advanceMode = advanceMode2;
    }
}
