import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="计算器+函数图像", page_icon="📊")

# ============ 背景音乐 ============
if "bgm_start" not in st.session_state:
    st.session_state.bgm_start = False
bgm_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

# ============ 页面切换 ============
page = st.sidebar.radio("选择功能", ["🧮 计算器", "📈 函数图像"])

# ==================== 页面1：计算器 ====================
if page == "🧮 计算器":
    st.title("简易网页计算器")
    num1 = st.number_input("请输入第一个数字")
    op = st.selectbox("运算符", ["+", "-", "*", "/"])
    num2 = st.number_input("请输入第二个数字")

    if st.button("开始计算"):
        if not st.session_state.bgm_start:
            st.session_state.bgm_start = True
        try:
            if op == "+":
                res = num1 + num2
            elif op == "-":
                res = num1 - num2
            elif op == "*":
                res = num1 * num2
            elif op == "/":
                if num2 == 0:
                    st.error("错误：除数不能为0")
                    res = None
                else:
                    res = num1 / num2
            if res is not None:
                st.success(f"结果：{num1} {op} {num2} = {res}")
        except Exception as e:
            st.error(f"出错：{e}")

# ==================== 页面2：函数图像 ====================
else:
    st.title("📈 函数图像绘制")
    st.write("输入函数表达式，拖动滑块改变 x 范围，图像实时更新")

    # 输入函数
    func_input = st.text_input("输入函数 y =", value="x**2",
                                help="支持：+ - * / **  sin(x) cos(x) tan(x) exp(x) log(x) sqrt(x) abs(x)  pi")

    # 自变量范围滑块（实时更新）
    col1, col2 = st.columns(2)
    with col1:
        x_min = st.slider("x 最小值", -50.0, 0.0, -10.0, 0.5)
    with col2:
        x_max = st.slider("x 最大值", 0.0, 50.0, 10.0, 0.5)

    if x_min >= x_max:
        st.error("x 最小值必须小于最大值")
    else:
        # 安全解析函数
        allowed = {
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "sqrt": np.sqrt,
            "abs": np.abs, "pi": np.pi, "e": np.e,
            "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan,
        }

        try:
            x = np.linspace(x_min, x_max, 1000)
            # 替换 ^ 为 **
            expr = func_input.replace("^", "**")
            y = eval(expr, {"__builtins__": {}}, {**allowed, "x": x})

            # 实时显示当前因变量范围
            y_min, y_max = float(np.nanmin(y)), float(np.nanmax(y))
            st.info(f"当前因变量 y 范围：[{y_min:.4f}, {y_max:.4f}]")

            # 绘图
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(x, y, color="#ff69b4", linewidth=2, label=f"y = {func_input}")
            ax.axhline(y=0, color="gray", linewidth=0.8, linestyle="--")
            ax.axvline(x=0, color="gray", linewidth=0.8, linestyle="--")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title(f"y = {func_input}")
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)

            # 显示数值表
            with st.expander("查看 x-y 数值表（前20个点）"):
                import pandas as pd
                df = pd.DataFrame({"x": x[:20], "y": y[:20]})
                st.dataframe(df)

        except Exception as e:
            st.error(f"函数解析错误：{e}")
            st.write("示例：`x**2`、`sin(x)`、`x**3 - 2*x`、`exp(-x**2)`")

# ============ 背景音乐播放 ============
if st.session_state.bgm_start:
    st.audio(bgm_url, format="audio/mpeg", loop=True, autoplay=True)
