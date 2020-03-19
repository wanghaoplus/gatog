#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))) #设置函数所在目录(上级目录)
print (sys.path[-1]) #打印设置目录
from autotest import main

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph.output import GraphvizOutput

Graphviz = GraphvizOutput(out_ = r'relitionship.png')
with PyCallGraph(output=Graphviz):
    #运行函数
    main()