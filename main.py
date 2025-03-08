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
    with st.expander("📖 Instructions", expanded=True):
        st.markdown("""
        1. Enter up to 999 stock symbols in the text area below
        2. Symbols can be separated by commas or newlines
        3. You can use NSE symbols with or without the "NSE:" prefix (e.g., both "RELIANCE" and "NSE:RELIANCE" work)
        4. Check "Show fundamentals and result dates" to view quarterly results dates and financial metrics
        5. Click 'Process Symbols' to get industry mappings and fundamental data
        6. Use the 'Copy Results' button to copy formatted output with NSE prefix added automatically
        7. Download the fundamentals data as CSV if needed
        """)

    try:
        mapper = get_mapper()
        stats = mapper.get_database_stats()

        # Display database statistics
        st.info(
            f"📊 Database loaded with {stats['total_symbols']:,} symbols mapped to "
            f"{stats['mapped_industries']} industries out of {stats['total_industries']} "
            f"available industry categories"
        )

        # Display available industries
        with st.expander("🏢 Available Industry Categories"):
            industries = mapper.get_available_industries()
            # Display in columns for better readability
            cols = st.columns(3)
            industries_per_col = len(industries) // 3 + 1
            for i, industry in enumerate(industries):
                cols[i // industries_per_col].text(f"• {industry}")

    except Exception as e:
        st.error(f"❌ Error loading industry database: {str(e)}")
        st.stop()

    # Input area
    symbols_input = st.text_area(
        "Enter stock symbols (max 999, separated by commas or newlines):",
        height=200,
        help="Example: RELIANCE, HDFCBANK, TCS or NSE:RELIANCE, NSE:HDFCBANK, NSE:TCS"
    )

    # Add option to show fundamentals
    show_fundamentals = st.checkbox("Show fundamentals and result dates", value=False,
                                   help="Display quarterly results date and fundamental data for the symbols")

    # Process button
    if st.button("Process Symbols", type="primary"):
        if not symbols_input.strip():
            st.error("Please enter some symbols to process.")
            return

        try:
            mapped_symbols, invalid_symbols = mapper.map_symbols(symbols_input)
            symbol_list = list(mapped_symbols.keys())

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
                    
                    # Add download button for search results
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results",
                        data=csv,
                        file_name="symbol_industry_mapping.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No valid symbols found.")

            with col2:
                st.subheader("TradingView Format")
                if mapped_symbols:
                    formatted_output = mapper.format_tv_output(mapped_symbols)
                    
                    # Display the code directly for visibility
                    st.code(formatted_output, language="text")
                    
                    # Create a non-interactive display with copy button
                    st.markdown(
                        f"""
                        <div style="position: relative;">
                            <pre style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; white-space: pre-wrap; overflow-x: auto;">{formatted_output}</pre>
                            <button id="copyButton" style="position: absolute; top: 10px; right: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; padding: 6px 12px; cursor: pointer;">
                                📋
                            </button>
                        </div>
                        <script>
                            const copyButton = document.getElementById('copyButton');
                            copyButton.addEventListener('click', function(e) {{
                                const text = `{formatted_output}`;
                                navigator.clipboard.writeText(text)
                                    .then(() => {{
                                        // Visual feedback without page refresh
                                        this.textContent = "✓";
                                        setTimeout(() => {{
                                            this.textContent = "📋";
                                        }}, 2000);
                                    }})
                                    .catch(err => console.error('Copy failed:', err));
                                    
                                // Prevent default button behavior
                                e.preventDefault();
                                e.stopPropagation();
                                return false;
                            }});
                        </script>
                        """,
                        unsafe_allow_html=True
                    )

            # Display fundamentals if option is selected
            if show_fundamentals and mapped_symbols:
                st.subheader("Fundamentals & Results Calendar")
                fundamentals_df = mapper.get_fundamentals_data(symbol_list)
                if not fundamentals_df.empty:
                    st.dataframe(
                        fundamentals_df,
                        hide_index=True,
                        use_container_width=True
                    )
                    # Add download button for fundamentals data
                    csv = fundamentals_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Fundamentals Data",
                        data=csv,
                        file_name="fundamentals_data.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No fundamental data found for the selected symbols.")

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
            <p>Built with Streamlit • Process up to 999 symbols at once</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()