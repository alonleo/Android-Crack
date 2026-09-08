# baseConfig.cmake — ASBuilder 内置 base::tool CMake 包配置（Prefab 兼容）
#
# 来源：com.fakerandroid.tools.build:support:1.0.38.aar 的 prefab（name=base, module=tool）
# 提供 hook 引擎实现：onJniLoad / baseImageAddr / fakeCpp / fakeDex（多 ABI libtool.a + include/faker.h）。
# 加载方式：CMakeLists.txt 直接 include 本文件（include "${CMAKE_CURRENT_LIST_DIR}/libs/baseConfig.cmake"）。

# base 包根目录 = 本 config 所在目录（cpp/libs/）
set(BASE_ROOT "${CMAKE_CURRENT_LIST_DIR}")

# 选择目标 ABI 对应的 libtool.a
if(ANDROID_ABI STREQUAL "arm64-v8a")
    set(_BASE_LIB "${BASE_ROOT}/prefab/modules/tool/libs/android.arm64-v8a/libtool.a")
elseif(ANDROID_ABI STREQUAL "armeabi-v7a")
    set(_BASE_LIB "${BASE_ROOT}/prefab/modules/tool/libs/android.armeabi-v7a/libtool.a")
elseif(ANDROID_ABI STREQUAL "x86")
    set(_BASE_LIB "${BASE_ROOT}/prefab/modules/tool/libs/android.x86/libtool.a")
elseif(ANDROID_ABI STREQUAL "x86_64")
    set(_BASE_LIB "${BASE_ROOT}/prefab/modules/tool/libs/android.x86_64/libtool.a")
else()
    message(FATAL_ERROR "base::tool: 不支持 ABI ${ANDROID_ABI}")
endif()

if(NOT TARGET base::tool)
    add_library(base::tool STATIC IMPORTED)
    set_target_properties(base::tool PROPERTIES
        IMPORTED_LOCATION "${_BASE_LIB}"
        INTERFACE_INCLUDE_DIRECTORIES "${BASE_ROOT}/prefab/modules/tool/include"
    )
endif()