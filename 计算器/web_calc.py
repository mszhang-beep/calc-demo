import streamlit as st

st.title("简易网页计算器")
exp = st.text_input("请输入计算表达式",value="")
try:
    if exp:
        ans = eval(exp)
        st.info(f"计算结果：{ans}")
except:
    st.error("表达式格式错误")

st.markdown("支持加减乘除括号，示例：`(100+20)*5`")