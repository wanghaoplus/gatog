#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph.output import GraphvizOutput

if __name__ == "__main__":

    sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))) #设置函数所在目录(上级目录)
    print (sys.path[-1]) #打印设置目录

    from autotest import main
    Graphviz = GraphvizOutput(out_ = r'relitionship.png')
    with PyCallGraph(output=Graphviz):
        #运行函数
        main()