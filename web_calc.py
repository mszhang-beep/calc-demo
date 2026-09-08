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
    st.title("📈 函数图像｜图像下方拖动滑块查看坐标")
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
    func1 = st.text_input("输入函数 y1 =", value="x**3")
    func2 = st.text_input("函数2 y2 =（留空只画y1）", value="log(2*x)")

    st.divider()
    st.markdown("### 📊绘制图像（手动设置X区间，点按钮更新曲线）")
    col1, col2 = st.columns(2)
    with col1:
        x_min = st.number_input("X轴最小值", value=0.01, step=0.1)
    with col2:
        x_max = st.number_input("X轴最大值", value=10.0, step=0.1)

    draw_btn = st.button("🖼️更新曲线图像")

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

    if st.session_state.curve_x is not None:
        st.markdown("### 🎯拖动滑块选择自变量 x")
        x_slide = st.slider("自变量 x", min_value=float(x_min), max_value=float(x_max), value=float((x_min+x_max)/2), step=0.01)

        y1_slide = None
        y2_slide = None
        y1_valid = False
        y2_valid = False

        expr_slide1 = auto_multiply(func1)
        try:
            y1_slide = eval(expr_slide1, {"__builtins__": {}}, {**allowed, "x": x_slide})
            y1_valid = np.isfinite(y1_slide)
        except Exception:
            y1_valid = False

        # 计算第二个函数的值（新增）
        if func2.strip() != "":
            expr_slide2 = auto_multiply(func2)
            try:
                y2_slide = eval(expr_slide2, {"__builtins__": {}}, {**allowed, "x": x_slide})
                y2_valid = np.isfinite(y2_slide)
            except Exception:
                y2_valid = False

        # 输出两个函数结果
        info_text = f"自变量 x = {x_slide:.4f}\n"
        if y1_valid:
            info_text += f"🔴 y1({x_slide:.2f}) = {y1_slide:.4f}\n"
        else:
            info_text += f"🔴 y1 在该x处无定义\n"

        if func2.strip() != "":
            if y2_valid:
                info_text += f"🔵 y2({x_slide:.2f}) = {y2_slide:.4f}"
            else:
                info_text += f"🔵 y2 在该x处无定义"

        st.info(info_text)

        fig2, ax2 = plt.subplots(figsize=(8,5))
        ax2.plot(st.session_state.curve_x, st.session_state.curve_y1, color="#ff69b4", linewidth=2, label=f"y1 = {func1}")
        if st.session_state.curve_y2 is not None:
            ax2.plot(st.session_state.curve_x, st.session_state.curve_y2, color="#1f77b4", linewidth=2, label=f"y2 = {func2}")

        for (px,py) in st.session_state.cross_points:
            ax2.plot(px, py, "ro", markersize=6)

        # 同一条竖线，标记两个函数的点
        ax2.axvline(x=x_slide, color="orange", linestyle="--", alpha=0.7)
        if y1_valid:
            ax2.plot(x_slide, y1_slide, "orange", marker="o", markersize=7, zorder=10)
        if func2.strip()!="" and y2_valid:
            ax2.plot(x_slide, y2_slide, "deepskyblue", marker="o", markersize=7, zorder=10)

        ax2.axhline(y=0, color="gray", linewidth=0.8, linestyle="--")
        ax2.axvline(x=0, color="gray", linewidth=0.8, linestyle="--")
        ax2.set_xlabel("x")
        ax2.set_ylabel("y")
        ax2.set_title("函数图像｜橙色=y1点，蓝色=y2点")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

        if len(st.session_state.cross_points) > 0:
            st.success(f"✅找到 {len(st.session_state.cross_points)} 个交点：")
            for px, py in st.session_state.cross_points:
                st.write(f"交点：x = {px}, y = {py}")

        with st.expander("查看 x‑y 数值表（前20个点）"):
            if st.session_state.curve_y2 is not None:
                df = pd.DataFrame({
                    "x": st.session_state.curve_x[:20],
                    "y1": st.session_state.curve_y1[:20],
                    "y2": st.session_state.curve_y2[:20]
                })
            else:
                df = pd.DataFrame({"x": st.session_state.curve_x[:20], "y1": st.session_state.curve_y1[:20]})
            st.dataframe(df)

st.divider()
st.caption("制作人：一叶知秋.")
