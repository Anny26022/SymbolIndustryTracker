import streamlit as st
from utils.data_processor import IndustryMapper
import pandas as pd

# Initialize the IndustryMapper
@st.cache_resource
def get_mapper():
    return IndustryMapper()

def main():
    st.set_page_config(
        page_title="Stock Symbol Industry Mapper",
        page_icon="📈",
        layout="wide"
    )

    st.title("📈 Stock Symbol Industry Mapper")
    
    # Instructions
    with st.expander("📖 Instructions", expanded=False):
        st.markdown("""
        1. Enter up to 900 stock symbols in the text area below
        2. Symbols can be separated by commas or newlines
        3. Click 'Process Symbols' to get industry mappings
        4. Use the 'Copy Results' button to copy formatted output
        """)

    # Input area
    symbols_input = st.text_area(
        "Enter stock symbols (max 900, separated by commas or newlines):",
        height=200,
        help="Example: AAPL, MSFT, GOOGL"
    )

    # Process button
    if st.button("Process Symbols", type="primary"):
        if not symbols_input.strip():
            st.error("Please enter some symbols to process.")
            return

        try:
            mapper = get_mapper()
            mapped_symbols, invalid_symbols = mapper.map_symbols(symbols_input)

            # Display results in columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Results")
                if mapped_symbols:
                    # Create a DataFrame for better display
                    results_df = pd.DataFrame(
                        list(mapped_symbols.items()),
                        columns=['Symbol', 'Industry']
                    )
                    st.dataframe(
                        results_df,
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("No valid symbols found.")

            with col2:
                st.subheader("TradingView Format")
                if mapped_symbols:
                    formatted_output = mapper.format_tv_output(mapped_symbols)
                    st.code(formatted_output, language="text")
                    
                    # Copy button
                    st.button(
                        "📋 Copy Results",
                        on_click=lambda: st.write(
                            f'<script>navigator.clipboard.writeText("{formatted_output}");</script>',
                            unsafe_allow_html=True
                        )
                    )

            # Display invalid symbols if any
            if invalid_symbols:
                st.error(
                    f"Invalid or unmapped symbols ({len(invalid_symbols)}): "
                    f"{', '.join(invalid_symbols)}"
                )

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Built with Streamlit • Process up to 900 symbols at once</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
