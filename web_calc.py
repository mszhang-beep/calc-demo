import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re   # ❗这一行千万不能丢

st.set_page_config(page_title="计算器+函数图像", page_icon="📊")

# ============ 侧边栏页面切换 ============
page = st.sidebar.radio("选择功能", ["🧮 计算器", "📈 函数图像"])

# ==================== 页面1：计算器 ====================
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

# ==================== 页面2：函数图像绘图 ====================
else:
    st.title("📈 函数图像绘制（支持求交点）")
    st.write("输入两个函数，可手动填写或拖动滑块调整范围，支持复合函数、log10、cot，自动标记交点")
    st.caption("💡 乘法可以省略乘号，直接写 2x、3sin(x) 也能识别")

    example_list = [
        "x**2",
        "sin(x**2)",
        "cos(exp(x))",
        "sqrt(x**2+4)",
        "sin(cos(x))",
        "log10(x+5)",
        "1/(1+exp(-x))"
    ]
    select_func = st.selectbox("函数示例参考", example_list)
    func1 = st.text_input("输入函数1 y1 =", value="log(2x)",
                                help="例：sin(x**2)、log10(x+5)、cot(x)、2x")
    func2 = st.text_input("输入函数2 y2 =", value="2x",
                                help="求 y1=y2 的交点")

    # ===== session_state 双向同步滑块与输入框 =====
    if "x_min" not in st.session_state:
        st.session_state.x_min = -100.0
    if "x_max" not in st.session_state:
        st.session_state.x_max = 100.0

    def sync_x_min_input():
        st.session_state.x_min = st.session_state.x_min_input
    def sync_x_min_slider():
        st.session_state.x_min = st.session_state.x_min_slider
    def sync_x_max_input():
        st.session_state.x_max = st.session_state.x_max_input
    def sync_x_max_slider():
        st.session_state.x_max = st.session_state.x_max_slider

    col_a, col_b = st.columns(2)
    with col_a:
        x_min_input = st.number_input("手动输入X最小值", value=st.session_state.x_min,
                                       min_value=-10000.0, max_value=10000.0,
                                       key="x_min_input", on_change=sync_x_min_input)
        x_min = st.slider("x最小值滑块", -10000.0, 10000.0, st.session_state.x_min, 50.0,
                           key="x_min_slider", on_change=sync_x_min_slider)
    with col_b:
        x_max_input = st.number_input("手动输入X最大值", value=st.session_state.x_max,
                                       min_value=-10000.0, max_value=10000.0,
                                       key="x_max_input", on_change=sync_x_max_input)
        x_max = st.slider("x最大值滑块", -10000.0, 10000.0, st.session_state.x_max, 50.0,
                           key="x_max_slider", on_change=sync_x_max_slider)

    if x_min >= x_max:
        st.error("x 最小值必须小于最大值")
    else:
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

        # 自动补乘号处理 2x →2*x
        def auto_multiply(expr):
            expr = expr.replace("^", "**")
            expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
            expr = re.sub(r'(\))([a-zA-Z(])', r'\1*\2', expr)
            return expr

        try:
            x = np.linspace(x_min, x_max, 2000)
            expr1 = auto_multiply(func1)
            expr2 = auto_multiply(func2)
            y1 = eval(expr1, {"__builtins__": {}}, {**allowed, "x": x})
            y2 = eval(expr2, {"__builtins__": {}}, {**allowed, "x": x})

            diff = y1 - y2
            cross_idx = np.where(np.diff(np.sign(diff)))[0]
            cross_points = []
            for idx in cross_idx:
                x0 = x[idx]
                y0 = y1[idx]
                cross_points.append((round(x0, 4), round(y0, 4)))

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(x, y1, color="#ff69b4", linewidth=2, label=f"y1 = {func1}")
            ax.plot(x, y2, color="#1f77b4", linewidth=2, label=f"y2 = {func2}")
            for (px, py) in cross_points:
                ax.plot(px, py, "ro", markersize=6)

            ax.axhline(y=0, color="gray", linewidth=0.8, linestyle="--")
            ax.axvline(x=0, color="gray", linewidth=0.8, linestyle="--")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title("函数图像与交点")
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)

            if len(cross_points) > 0:
                st.success(f"✅找到 {len(cross_points)} 个交点：")
                for px, py in cross_points:
                    st.write(f"交点：x = {px}, y = {py}")
            else:
                st.info("当前区间内没有找到交点，可以调整X范围再试")

            with st.expander("查看 x-y 数值表（前20个点）"):
                df = pd.DataFrame({"x": x[:20], "y1": y1[:20], "y2": y2[:20]})
                st.dataframe(df)

        except Exception as e:
            st.error(f"函数解析错误：{e}")
            st.write("示例：`log10(x+5)`、`cot(x)`、`sin(x**2)`、`2x` 都支持")


# ========== 页面底部：制作人署名 ==========
st.divider()
st.caption("制作人：一叶知秋.")
