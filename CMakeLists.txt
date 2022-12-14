cmake_minimum_required(VERSION 3.23)
project(AroAceLang)

find_package(LLVM REQUIRED CONFIG)
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

set(CMAKE_CXX_STANDARD 23)
add_compile_options(-Wall -Wextra -pedantic -Werror)

include_directories(${LLVM_INCLUDE_DIRS})
separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})
add_definitions(${LLVM_DEFINITIONS_LIST})

# JSON:
set(JSON_BuildTests OFF CACHE INTERNAL "")
add_subdirectory(nlohmann_json)

add_executable(AroAceLang main.cpp)

llvm_map_components_to_libnames(llvm_libs support core irreader)

target_link_libraries(AroAceLang ${llvm_libs} nlohmann_json::nlohmann_json)
