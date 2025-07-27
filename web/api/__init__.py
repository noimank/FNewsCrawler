#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块

包含所有API路由的定义
"""

from .login import router as login_router
from .crawler import router as crawler_router

__all__ = ["login_router", "crawler_router"]