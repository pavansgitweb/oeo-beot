{pkgs}: {
  deps = [
    pkgs.libopus
    pkgs.ffmpeg.bin
    pkgs.zlib
    pkgs.tk
    pkgs.tcl
    pkgs.openjpeg
    pkgs.libxcrypt
    pkgs.libwebp
    pkgs.libtiff
    pkgs.libjpeg
    pkgs.libimagequant
    pkgs.lcms2
    pkgs.freetype
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libopus
      pkgs.zlib
      pkgs.tk
      pkgs.tcl
      pkgs.openjpeg
      pkgs.libxcrypt
      pkgs.libwebp
      pkgs.libimagequant
      pkgs.freetype
    ];
  };
}
