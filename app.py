import streamlit as st
import streamlit.components.v1 as components
from hsplayer import agent
from hsplayer.agent import Agent

st.markdown(
"""
<style>
.stream-box {
    height:500px;
    overflow-y:auto;
    border:1px solid #ccc;
    border-radius:6px;
    padding:10px;
    font-family:monospace;
    background:#0e1117;
    color:#fafafa;
    white-space:pre-wrap;
    word-break:break-all;
}
</style>

<script>
function scrollToBottom(){
    const box = window.parent.document.querySelector('.stream-box');
    if(box){
        box.scrollTop = box.scrollHeight;
    }
}
</script>
""",
unsafe_allow_html=True
)

if "editable_text" not in st.session_state:
    st.session_state.editable_text = "点击左侧按钮生成初始内容..."
    
if 'agent' not in st.session_state:
    st.session_state.agent = Agent()
    st.success("Agent 已初始化！")
PPagent = st.session_state.agent 

# 1. 页面基础配置
st.set_page_config(
    page_title="LLM Agent 工作台",
    page_icon="⚡",
    layout="wide"
)

# 3. --- 主内容区域 ---
st.title("⚡ PPagent 控制台")

with st.expander("当前节点", expanded=True):
    st.write(f"节点编号: {PPagent.current_node.id}, 历史动作: {PPagent.get_action_history(PPagent.current_node)}")

col_prompt, col_answer = st.columns([1, 1]) 

with col_prompt:
    col1, col2 = st.columns([1, 3])
    with col1:
        prompt_button = st.button("A: 生成内容", use_container_width=True)
    with col2:
        info = st.empty()

    if prompt_button:
        PPagent.reinit()  # 重新解析日志，更新世界状态

        with st.spinner("正在生成内容..."):
            result = PPagent.get_prompt()
            st.session_state.editable_text = result
            info.success("内容已生成！请在下方修改。")


    st.text_area(
    "编辑提示词",
    key = "editable_text",
    height=600
    )   

with col_answer:    
    response_container = st.container()
    answer_button = st.button("B: 提交修改后的内容")
    placeholder = st.empty()
    if answer_button:

        user_modified_content = st.session_state.editable_text
        full_response = ""

        with st.spinner("Agent 正在思考并生成中..."):
            try:
                for chunk in PPagent.generate_response(user_modified_content):
                    full_response += chunk
                    placeholder.markdown(
                        f"""
                        <div class="stream-box">{full_response}</div>
                        <script>scrollToBottom()</script>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"发生错误: {e}")

if PPagent.response:
    placeholder.empty()
    
    with placeholder.container():
        with st.expander("📄 plan", expanded=True):
            st.write(PPagent.response.get("plan", "无行动内容"))
        with st.expander("📄 actions", expanded=True):
            if not PPagent.next_actions:
                st.info("暂无待确认的动作。")
            else:
                st.markdown("请审核以下生成的动作：")
                for node_id, action_text in PPagent.next_actions.items():
                    if not PPagent.action_tree.search_id(node_id).valid:
                        continue
                    col_text, col_btns = st.columns([3, 1])
                    with col_text:
                        st.markdown(f"**{node_id}**: {action_text}")

                    with col_btns:
                        sub_col1, sub_col2 = st.columns(2)
                        with sub_col1:
                            if st.button("✓", key=f"yes_{node_id}", use_container_width=True):
                                PPagent.set_action(node_id)
                                st.rerun()
                        with sub_col2:
                            if st.button("✗", key=f"no_{node_id}", use_container_width=True):
                                PPagent.delete_action(node_id)
                                st.rerun()
        with st.expander("📄 thinking", expanded=False):
            st.write(PPagent.response.get("thinking", "无分析内容"))

        with st.expander("当前路径", expanded=True):
            st.write(PPagent.get_action_history(PPagent.current_node))

# 4. (可选) 底部展示一些调试信息或元数据
with st.expander("查看当前配置详情"):
    st.json(PPagent.export_action_tree(), expanded=True)


# 5. (可选) 添加一些交互式组件来调整参数或触发特定行为
st.subheader("⚙️ 调整参数")
col_num, col_op, col_arg, col_btn = st.columns([1, 1, 2, 1], gap="small")
with col_num:
    num_val = st.number_input("id", min_value=0, step=1, key="input_num")
with col_op:
    op_val = st.selectbox("执行", ["set","add", "delete"], key="input_op")
with col_arg:
    str_val = st.text_input("参数", placeholder="", key="input_str")
with col_btn:
    clicked = st.button("执行", type="primary", use_container_width=True, key="btn_run")
if clicked:
    if op_val == "add":
        if not str_val:
            st.error("❌ 第三个参数不能为空！")
        else:
            PPagent.add_action(num_val, str_val)
    elif op_val == "delete":
        PPagent.delete_action(num_val)
    else:
        PPagent.set_action(num_val)
    st.success(f"✅ 已执行 {op_val} 操作！")
    st.rerun()