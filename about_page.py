# about_page.py
import streamlit as st

def about_page():
    st.title("[개인 맞춤 진로 추천 시스템]")
    st.markdown("#### '당신만의 길을 찾아, 진정한 행복을 발견하세요'")

    st.markdown("#### '내가 무엇을 할 때 가장 행복한가? 나에게 희열을 느끼게 하는 일은 무엇인가?' - 조셉 캠벨")

    st.header("개인 맞춤 진로 탐색")
    st.write("""
        당신이 진정으로 행복하고 열정적인 일을 찾도록 도와줍니다. 
        조셉 캠벨이 말한 '내가 무엇을 할 때 가장 행복한가?'에 대한 답을 찾아보세요. 
        당신의 취미, 흥미, 목표를 기반으로 당신만의 길을 개척하는데 도움을 줍니다.
    """)

    st.header("자신만의 길 탐험")
    st.write("""
        "먼 훗날에 나는 어디선가 한숨을 쉬며 이야기할 것입니다. 
        숲속에 두 갈래 길이 있었다고, 나는 사람이 적게 간 길을 택하였다고, 
        그리고 그것이 내 모든 것을 바꾸어 놓았다고." 
        -- 로버트 프로스트 --
    """)

    st.markdown("""
        "어둠이 짙게 깔린 숲으로 들어가라. 그곳에는 어떤 길도 나 있지 않다. 길이 있다면 그것은 다른 사람의 길이다. 
        각각의 인간 존재는 고유하다. 중요한 것은 자신만의 블리스를 향해 가는 길을 발견하는 것이다."
        -- 조셉 캠벨 --
    """)