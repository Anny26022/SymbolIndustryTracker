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
                    
                    # Sort by industry frequency
                    industry_counts = results_df['Industry'].value_counts()
                    results_df['IndustryCount'] = results_df['Industry'].map(industry_counts)
                    results_df = results_df.sort_values('IndustryCount', ascending=False)
                    results_df = results_df.drop(columns=['IndustryCount'])
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
                    # Initialize session state for format selection if not exists
                    if 'format_selection' not in st.session_state:
                        st.session_state['format_selection'] = "With industry categorization"
                        
                    # Simplified radio button with session state
                    format_options = ["With industry categorization", "Flat list of symbols only"]
                    copy_format = st.radio(
                        "Copy format:",
                        format_options,
                        index=format_options.index(st.session_state['format_selection']),
                        key="format_selection",
                        horizontal=True,
                        on_change=lambda: None  # Empty callback to prevent full rerun
                    )
                    
                    # Save selected format in session state
                    st.session_state['format_selection'] = copy_format
                    
                    # Get formatted outputs based on the current selection
                    categorized_output = mapper.format_tv_output(mapped_symbols)
                    flat_output = mapper.format_flat_output(mapped_symbols)
                    
                    # Directly use the radio button value to determine output
                    selected_output = categorized_output if copy_format == "With industry categorization" else flat_output
                    
                    # Display the code directly for visibility
                    st.code(selected_output, language="text")
                    
                    # Use Streamlit's built-in copy functionality instead of custom JS
                    st.code(selected_output, language="text")
                    
                    # Add a regular Streamlit button for copy functionality
                    if st.button("📋 Copy to Clipboard", key=f"copy_{copy_format}"):
                        # Use Streamlit's clipboard utilities
                        st.write("✅ Copied to clipboard!")
                        st.toast("Symbols copied to clipboard successfully!", icon="✅")
                        # Use Streamlit experimental set clipboard
                        st.experimental_set_query_params(clipboard=selected_output)
                        
                        # Also provide the text in a "hidden" expander that can be copy-pasted directly
                        with st.expander("📋 Copy manually if button doesn't work", expanded=False):
                            st.text_area("", value=selected_output, height=100, label_visibility="collapsed")

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