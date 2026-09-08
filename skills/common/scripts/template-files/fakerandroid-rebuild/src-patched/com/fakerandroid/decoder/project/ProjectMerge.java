package com.fakerandroid.decoder.project;

import com.fakerandroid.decoder.util.PatchUtil;
import java.io.File;
import java.io.IOException;

/* JADX INFO: loaded from: ProjectMerge.class */
public class ProjectMerge {
    public static void copyProject(File out) throws IOException {
        PatchUtil.copyDirFromJar("/project/", out.getAbsolutePath());
    }
}
