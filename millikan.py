import streamlit as st
import pandas as pd
import math

# --- 页面设置 ---
st.set_page_config(page_title="密里根油滴实验计算", layout="wide")

st.title("🧪 密里根油滴实验数据处理 SHNU-PHY Lab")
st.markdown("请在左侧输入实验参数，并在下方录入测量数据。")

# --- 物理逻辑函数 ---
def calculate_millikan(tf, U, tr, method, d, l):
    # 物理常量
    g = 9.8015
    rho_oil = 981.0
    rho_air = 1.205
    eta = 1.83e-5
    b = 6.17e-6
    p = 76.0
    e_std = 1.602176634e-19

    vf = l / tf
    r = math.sqrt((9 * eta * vf) / (2 * (rho_oil - rho_air) * g))
    
    if "静态" in method:
        q_raw = ((4/3) * math.pi * (r**3) * (rho_oil - rho_air) * g * d) / U
    else:
        vr = l / tr
        q_raw = (6 * math.pi * eta * r * (vf + vr) * d) / U
    
    # 库宁汉修正
    q = q_raw / math.pow(1 + (b / (p * r)), 1.5)
    n = round(q / e_std)
    e_calc = q / n if n != 0 else 0
    return r, q, n, e_calc

# --- 侧边栏：设置仪器参数 ---
with st.sidebar:
    st.header("⚙️ 仪器参数")
    d_mm = st.number_input("极板间距 d (mm)", value=5.00, step=0.01)
    l_mm = st.number_input("测量距离 l (mm)", value=1.50, step=0.01)
    d = d_mm / 1000.0
    l = l_mm / 1000.0

# --- 初始化数据存储 ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 输入区域 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📥 录入数据")
    method = st.selectbox("选择方法", ["静态法 (平衡法)", "动态法 (升降法)"])
    u_val = st.number_input("平衡/上升电压 U (V)", value=250.0, step=1.0)
    tf_val = st.number_input("下落时间 tf (s)", value=15.0, step=0.1)
    
    tr_val = 0.0
    if "动态" in method:
        tr_val = st.number_input("上升时间 tr (s)", value=10.0, step=0.1)
    
    if st.button("➕ 开始计算"):
        r, q, n, e_calc = calculate_millikan(tf_val, u_val, tr_val, method, d, l)
        st.session_state.history.append({
            "方法": method[:2],
            "U (V)": u_val,
            "tf (s)": tf_val,
            "tr (s)": tr_val if "动态" in method else "-",
            "半径 r (m)": f"{r:.4e}",
            "电荷 q (C)": f"{q:.4e}",
            "电子数 n": n,
            "单电子 e": f"{e_calc:.4e}"
        })

with col2:
    st.subheader("📊 结果表格")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.table(df)
        
        if st.button("🗑️ 清空表格"):
            st.session_state.history = []
            st.rerun()
        
        # 计算平均值
        e_list = [float(item["单电子 e"]) for item in st.session_state.history]
        if e_list:
            avg_e = sum(e_list) / len(e_list)
            st.metric("平均单电子电量", f"{avg_e:.4e} C")
            error = abs(avg_e - 1.602e-19) / 1.602e-19 * 100
            st.write(f"相对误差: **{error:.2f}%**")
    else:
        st.info("暂无数据，请在左侧录入。")
