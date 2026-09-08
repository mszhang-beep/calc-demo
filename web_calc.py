import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re

st.set_page_config(page_title="计算器+函数图像", page_icon="📊")

page = st.sidebar.radio("选择功能", ["🧮 计算器", "📈 函数图像"])

if page == "🧮 计算器":
    st.title("简易网页计算器")
    num1 = st.number_input("请输入第一个数字")
    op = st.selectbox("运算符", ["+", "-", "*", "/"])
    num2 = st.number_input("请输入第二个数字")
    if st.button("开始计算"):
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

else:
    st.title("📈 函数图像｜滑动x实时看坐标点")
    st.write("函数2留空，仅绘制单个函数；填写两个函数绘图+求交点")
    st.caption("💡乘法省略乘号写2x；log/log10括号内必须>0")

    example_list = [
        "x**2",
        "sin(x**2)",
        "cos(exp(x))",
        "sqrt(x**2+4)",
        "sin(cos(x))",
        "log10(x+5)",
        "x**3"
    ]
    select_func = st.selectbox("函数示例参考", example_list)
    func1 = st.text_input("输入函数 y =", value="x**3")
    func2 = st.text_input("函数2 y2 =（留空只画y1）", value="")

    # 滑动自变量
    st.markdown("### 🎯拖动滑块，自变量x，实时显示y，图上标记当前点")
    x_slide = st.slider("自变量 x", min_value=-20.0, max_value=20.0, value=1.0, step=0.01)

    allowed = {
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "exp": np.exp, "log": np.log, "log10": np.log10, "sqrt": np.sqrt,
        "abs": np.abs, "pi": np.pi, "e": np.e,
        "cot": lambda x: 1 / np.tan(x),
        "sec": lambda x: 1 / np.cos(x),
        "csc": lambda x: 1 / np.sin(x)
    }

    def auto_multiply(expr):
        expr = expr.replace("^", "**")
        expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
        expr = re.sub(r'(\))([a-zA-Z(])', r'\1*\2', expr)
        return expr

    # 滑块实时求值
    y_slide = None
    slide_valid = False
    try:
        expr_slide = auto_multiply(func1)
        y_slide = eval(expr_slide, {"__builtins__": {}}, {**allowed, "x": x_slide})
        slide_valid = np.isfinite(y_slide)
        if slide_valid:
            st.info(f"当 x = {x_slide:.4f} 时，y = {y_slide:.4f}")
        else:
            st.warning(f"当前x={x_slide}，该位置函数无定义")
    except Exception:
        st.warning(f"当前x={x_slide}，该位置函数无定义")

    st.divider()
    st.markdown("### 📊绘制图像（手动设置X区间，点按钮更新曲线）")
    col1, col2 = st.columns(2)
    with col1:
        x_min = st.number_input("X轴最小值", value=-5.0, step=0.1)
    with col2:
        x_max = st.number_input("X轴最大值", value=5.0, step=0.1)

    draw_btn = st.button("🖼️更新曲线图像")

    # 使用session_state保存曲线数据，滑块变动时只叠加标记点，不重绘整条曲线
    if "curve_x" not in st.session_state:
        st.session_state.curve_x = None
        st.session_state.curve_y1 = None
        st.session_state.curve_y2 = None
        st.session_state.cross_points = []

    if draw_btn:
        if x_min >= x_max:
            st.error("x 最小值必须小于最大值")
        else:
            try:
                x = np.linspace(x_min, x_max, 2000)
                expr1 = auto_multiply(func1)
                y1 = eval(expr1, {"__builtins__": {}}, {**allowed, "x": x})
                mask = np.isfinite(y1)
                st.session_state.curve_x = x[mask]
                st.session_state.curve_y1 = y1[mask]
                st.session_state.curve_y2 = None
                st.session_state.cross_points = []

                if func2.strip() != "":
                    expr2 = auto_multiply(func2)
                    y2 = eval(expr2, {"__builtins__": {}}, {**allowed, "x": x})
                    mask2 = np.isfinite(y2)
                    st.session_state.curve_y2 = y2[mask2]
                    x2 = x[mask2]
                    y1_2 = y1[mask2]
                    diff = y1_2 - st.session_state.curve_y2
                    cross_idx = np.where(np.diff(np.sign(diff)))[0]
                    cp = []
                    for idx in cross_idx:
                        x0 = x2[idx]
                        y0 = y1_2[idx]
                        cp.append((round(x0,4), round(y0,4)))
                    st.session_state.cross_points = cp

            except Exception as e:
                st.error(f"函数解析错误：{e}")

    # 只要曲线数据存在，就绘图，并且叠加滑块当前位置标记
    if st.session_state.curve_x is not None:
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(st.session_state.curve_x, st.session_state.curve_y1, color="#ff69b4", linewidth=2, label=f"y = {func1}")
        if st.session_state.curve_y2 is not None:
            ax.plot(st.session_state.curve_x, st.session_state.curve_y2, color="#1f77b4", linewidth=2, label=f"y2 = {func2}")

        # 交点红点
        for (px,py) in st.session_state.cross_points:
            ax.plot(px, py, "ro", markersize=6)

        # 动态标记：滑块对应的竖线+圆点
        if slide_valid and y_slide is not None:
            ax.axvline(x=x_slide, color="orange", linestyle="--", alpha=0.7)
            ax.plot(x_slide, y_slide, "orange", marker="o", markersize=7, zorder=10, label=f"当前点({x_slide:.2f},{y_slide:.2f})")

        ax.axhline(y=0, color="gray", linewidth=0.8, linestyle="--")
        ax.axvline(x=0, color="gray", linewidth=0.8, linestyle="--")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("函数图像｜橙色标记为滑块当前位置")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        if len(st.session_state.cross_points) > 0:
            st.success(f"✅找到 {len(st.session_state.cross_points)} 个交点：")
            for px, py in st.session_state.cross_points:
                st.write(f"交点：x = {px}, y = {py}")

        with st.expander("查看 x‑y 数值表（前20个点）"):
            df = pd.DataFrame({"x": st.session_state.curve_x[:20], "y": st.session_state.curve_y1[:20]})
            st.dataframe(df)

st.divider()
st.caption("制作人：一叶知秋.")
