# app.py 내의 tab1 부분 수정본
with tab1:
    st.subheader("📖 레시피 정밀 분석")
    uploaded_file = st.file_uploader("파일을 올려주세요", type=["xlsx", "pdf", "csv"])
    
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            # 셰프님 엑셀의 병합된 셀이나 제목줄을 무시하고 실제 데이터부터 읽도록 수정
            df = pd.read_excel(uploaded_file, header=0) # 첫 줄을 제목으로 인식
            st.write("### 📋 분석된 레시피 항목")
            st.dataframe(df.dropna(how='all', axis=1)) # 텅 빈 열은 숨기고 출력
            
        elif uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                # 표(Table) 위주로 추출하도록 로직 변경
                table = pdf.pages[0].extract_table()
                if table:
                    df_pdf = pd.DataFrame(table[1:], columns=table[0])
                    st.table(df_pdf)
                else:
                    st.text_area("텍스트 추출 내용", pdf.pages[0].extract_text())
