INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_GNU_FLEX gnu_flex)

FIND_PATH(
    GNU_FLEX_INCLUDE_DIRS
    NAMES gnu_flex/api.h
    HINTS $ENV{GNU_FLEX_DIR}/include
        ${PC_GNU_FLEX_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GNU_FLEX_LIBRARIES
    NAMES gnuradio-gnu_flex
    HINTS $ENV{GNU_FLEX_DIR}/lib
        ${PC_GNU_FLEX_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnu_flexTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GNU_FLEX DEFAULT_MSG GNU_FLEX_LIBRARIES GNU_FLEX_INCLUDE_DIRS)
MARK_AS_ADVANCED(GNU_FLEX_LIBRARIES GNU_FLEX_INCLUDE_DIRS)
