{ pkgs ? import <nixpkgs> { } }:


let
  lib = pkgs.lib;

  pythonPackages = pkgs.python3Packages;

  networkit = pythonPackages.buildPythonPackage rec {
    pname = "networkit";
    version = "11.0";
    dontUseCmakeConfigure = true;
    doCheck = false;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "0mwdfzw00w1158q12d6mqfz38bccsnr5xibm5p8zi9dkff4fnin4";
    };
    nativeBuildInputs = with pkgs; [
      gcc
      cmake
      (with pythonPackages; [
        cython
        numpy
        setuptools
        wheel
      ])
    ];
    propagatedBuildInputs = with pythonPackages; [
      scipy
      numpy
    ];
  };

  textblob = pythonPackages.buildPythonPackage rec {
    pname = "textblob";
    version = "0.18.0.post0";
    format = "pyproject";
    doCheck = false;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "8131c52c630bcdf61d04c359f939c98d5b836a01fba224d9e7ae22fc274e0ccb";
    };
    nativeBuildInputs = with pythonPackages; [ flit-core ];
    propagatedBuildInputs = with pythonPackages; [ nltk ];
  };

  textblob-fr = pythonPackages.buildPythonPackage rec {
    pname = "textblob-fr";
    version = "0.2.0";
    format = "setuptools";
    doCheck = false;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1edc942d018ae7cc121e59ec6bda7c33ece92943f81f9c9acc57a23a67897c33";
    };
    propagatedBuildInputs = [ textblob ];
  };

  fr-core-news-md = pythonPackages.buildPythonPackage rec {
    pname = "fr_core_news_md";
    version = "3.7.0";
    format = "setuptools";
    doCheck = false;
    src = pkgs.fetchurl {
      url = https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.7.0/fr_core_news_md-3.7.0.tar.gz;
      sha256 = "184gxwgf980x3vsn45zycd3cr1mkl3r1vbf3hb5hrhs8xk3y1v34";
    };
    propagatedBuildInputs = with pythonPackages; [ spacy ];
  };

  sphinx-press-theme = pythonPackages.buildPythonPackage rec {
    pname = "sphinx_press_theme";
    version = "0.9.1";
    format = "setuptools";
    doCheck = false;
    src = pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1643dee7365f7831d1d3971b389b7c255641a7aced75f0681f71574e380046cf";
    };
    propagatedBuildInputs = with pythonPackages; [ sphinx ];
  };

  my-packages = with pythonPackages; [
    pytest
    pytest-mock
    pytest-asyncio
    coverage

    discordpy

    networkit
    pygraphviz
    pandas

    matplotlib
    pillow

    transformers
    torch
    sentencepiece
    sacremoses
    protobuf

    textblob
    textblob-fr
    emoji
    nltk
    spacy
    scikit-learn
    fr-core-news-md

    sphinx
    myst-parser
    sphinx-press-theme

    feedparser
  ];

  my-packages-req = map (x: x.pname + "==" + x.version) (lib.filter (x: x.pname != "fr_core_news_md") my-packages);

  tex = (pkgs.texlive.combine {
    inherit (pkgs.texlive) scheme-medium
      latexmk fncychap wrapfig capt-of framed upquote needspace tabulary
      varwidth titlesec tocloft;
  });

in
pkgs.mkShell {
  name = "Convolyzer";

  packages = with pkgs; [
    (pythonPackages.python.withPackages (ps: my-packages))

    tex
  ];

  shellHook = ''
    echo "${lib.concatStringsSep "\n" my-packages-req}" > requirements.txt
  '';

}
