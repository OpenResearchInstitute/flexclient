# Install script for directory: /mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/gnu_flex" TYPE FILE FILES "/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/cmake/Modules/gnu_flexConfig.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/include/gnu_flex/cmake_install.cmake")
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/lib/cmake_install.cmake")
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/apps/cmake_install.cmake")
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/docs/cmake_install.cmake")
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/swig/cmake_install.cmake")
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/python/cmake_install.cmake")
  include("/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/grc/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
