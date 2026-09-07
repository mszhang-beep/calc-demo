import streamlit as st

st.title("简易网页计算器")
exp = st.text_input("请输入计算表达式", value="")
try:
    if exp:
        ans = eval(exp)
        st.info(f"计算结果：{ans}")
except:
    st.error("表达式格式错误")

st.markdown("支持加减乘除括号，示例：`(100+20)*5`")

st.divider()
avatar_url = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
html_text = f"""
<div style="display:flex;align-items:center;gap:8px">
< img src="{avatar_url}" width="36" height="36">
<span style="font-size:14px;color:#666">简易计算器 | 制作者：Ms.Zhang</span>
</div>
"""
st.markdown(html_text, unsafe_allow_html=True)
