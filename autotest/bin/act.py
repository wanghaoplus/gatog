#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/23 21:02
# @Author  : shaochanghong
# @Site    : 
# @File    : act.py
# @Software: PyCharm


def main():
    from autotest.core.running.TestProject import TestProject
    runProject = TestProject()
    runProject.setup()
    runProject.run()


if __name__ == "__main__":
    main()