cmake_minimum_required(VERSION 3.6)
project(native-lib)

set(CMAKE_CXX_STANDARD 11)

file(GLOB native_src "${CMAKE_SOURCE_DIR}/*.cpp")
file(GLOB inlinehook_src "${CMAKE_SOURCE_DIR}/And64InlineHook/*.cpp")
add_library(
        native-lib
        SHARED
        ${native_src}
        ${inlinehook_src}
)

target_link_libraries(
        native-lib
        android
        z
        log
        dl)
