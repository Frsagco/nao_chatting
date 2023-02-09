cmake_minimum_required(VERSION 2.8)
project(NAOListen)

set(CMAKE_CXX_FLAGS "-D_GLIBCXX_USE_CXX11_ABI=0")
# #list(APPEND CMAKE_MODULE_PATH "/usr/local/lib/cmake/PahoMqttCpp")

set(_srcs allisten.cpp allisten.h main.cpp)
# set(_dir /naoqi/src/cpp/naoqi-sdk-1.14.5-linux32)

# include_directories(${_dir}/include)

# # include_directories(/usr/local/include)

# add_executable(allisten ${_srcs})
# target_include_directories(allisten PUBLIC ${_dir}/include)
# target_link_directories(allisten PUBLIC ${_dir}/lib)
# target_link_libraries(allisten ${Boost_LIBRARIES} alcommon alvalue qi alerror alaudio alextractor almemoryfastaccess)



find_package(qibuild)

# Create an executable named sayhelloworld,
# with the source file : sayhelloworld.cpp
qi_create_bin(allisten ${_srcs})

# Tell CMake that sayhelloworld depends on ALCOMMON.
# This will set the libraries to link sayhelloworld with,
# the include paths, and so on
qi_use_lib(allisten ALCOMMON ALAUDIO)