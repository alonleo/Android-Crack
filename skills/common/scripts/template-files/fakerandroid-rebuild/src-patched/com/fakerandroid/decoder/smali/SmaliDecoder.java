package com.fakerandroid.decoder.smali;

import java.io.File;
import java.io.IOException;
import org.jf.baksmali.Baksmali;
import org.jf.baksmali.BaksmaliOptions;
import org.jf.dexlib2.DexFileFactory;
import org.jf.dexlib2.Opcodes;
import org.jf.dexlib2.analysis.InlineMethodResolver;
import org.jf.dexlib2.dexbacked.DexBackedDexFile;
import org.jf.dexlib2.dexbacked.DexBackedOdexFile;
import org.jf.dexlib2.iface.MultiDexContainer;

/* JADX INFO: loaded from: SmaliDecoder.class */
public class SmaliDecoder {
    private final File mApkFile;
    private final File mOutDir;
    private final String mDexFile;
    private final boolean mBakDeb;
    private final int mApi;
    static final /* synthetic */ boolean $assertionsDisabled;

    static {
        $assertionsDisabled = !SmaliDecoder.class.desiredAssertionStatus();
    }

    public static void decode(File apkFile, File outDir, String dexName, boolean bakdeb, int api) throws DexToSmaliException {
        new SmaliDecoder(apkFile, outDir, dexName, bakdeb, api).decode();
    }

    private SmaliDecoder(File apkFile, File outDir, String dexName, boolean bakdeb, int api) {
        this.mApkFile = apkFile;
        this.mOutDir = outDir;
        this.mDexFile = dexName;
        this.mBakDeb = bakdeb;
        this.mApi = api;
    }

    private void decode() throws DexToSmaliException {
        MultiDexContainer.DexEntry entry;
        try {
            BaksmaliOptions options = new BaksmaliOptions();
            options.deodex = false;
            options.implicitReferences = false;
            options.parameterRegisters = true;
            options.localsDirective = true;
            options.sequentialLabels = true;
            options.debugInfo = this.mBakDeb;
            options.codeOffsets = false;
            options.accessorComments = false;
            options.registerInfo = 0;
            options.inlineResolver = null;
            int jobs = Runtime.getRuntime().availableProcessors();
            if (jobs > 6) {
                jobs = 6;
            }
            MultiDexContainer<? extends DexBackedDexFile> container = DexFileFactory.loadDexContainer(this.mApkFile, Opcodes.forApi(this.mApi));
            if (container.getDexEntryNames().size() == 1) {
                entry = container.getEntry(container.getDexEntryNames().get(0));
            } else {
                entry = container.getEntry(this.mDexFile);
            }
            if (entry == null) {
                entry = container.getEntry(container.getDexEntryNames().get(0));
            }
            if (!$assertionsDisabled && entry == null) {
                throw new AssertionError();
            }
            DexBackedDexFile dexFile = (DexBackedDexFile) entry.getDexFile();
            if (dexFile.supportsOptimizedOpcodes()) {
                throw new DexToSmaliException("Warning: You are disassembling an odex file without deodexing it.");
            }
            if (dexFile instanceof DexBackedOdexFile) {
                options.inlineResolver = InlineMethodResolver.createInlineMethodResolver(((DexBackedOdexFile) dexFile).getOdexVersion());
            }
            Baksmali.disassembleDexFile(dexFile, this.mOutDir, jobs, options);
        } catch (IOException ex) {
            throw new DexToSmaliException(ex);
        }
    }
}
