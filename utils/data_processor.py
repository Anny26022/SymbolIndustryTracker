import pandas as pd
from typing import List, Tuple, Dict
import io

class IndustryMapper:
    def __init__(self):
        # Initialize with empty mapping
        self.mapping_df = pd.DataFrame()
        self.mapping_dict = {}

        # Try to load default mapping if available
        try:
            self.load_default_mapping()
        except Exception:
            pass

    def load_default_mapping(self):
        """Load the default industry mapping database."""
        self.mapping_df = pd.read_csv('data/industry_mapping.csv')
        self.update_mapping_dict()

    def load_custom_mapping(self, file_content):
        """Load a custom industry mapping from uploaded file."""
        try:
            # Read the uploaded file
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))

            # Validate the CSV format
            required_columns = ['symbol', 'industry']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV must contain 'symbol' and 'industry' columns")

            # Update the mapping
            self.mapping_df = df
            self.update_mapping_dict()

            return len(self.mapping_df), list(self.mapping_df['industry'].unique())

        except Exception as e:
            raise ValueError(f"Error loading custom mapping: {str(e)}")

    def update_mapping_dict(self):
        """Update the internal mapping dictionary."""
        self.mapping_dict = dict(zip(
            self.mapping_df['symbol'].str.upper(),
            self.mapping_df['industry']
        ))

    def clean_symbols(self, symbols: str) -> List[str]:
        """Clean and validate input symbols."""
        # Split and clean symbols
        symbols = symbols.replace('\n', ',').replace(';', ',')
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]

        # Remove duplicates while preserving order
        seen = set()
        symbol_list = [x for x in symbol_list if not (x in seen or seen.add(x))]

        return symbol_list

    def map_symbols(self, symbols: str) -> Tuple[Dict[str, str], List[str]]:
        """Map symbols to industries and return mapping and invalid symbols."""
        if not self.mapping_dict:
            raise ValueError("No industry mapping database loaded. Please upload a mapping file.")

        clean_symbol_list = self.clean_symbols(symbols)

        if len(clean_symbol_list) > 900:
            raise ValueError("Maximum 900 symbols allowed per batch")

        mapped_symbols = {}
        invalid_symbols = []

        for symbol in clean_symbol_list:
            if symbol in self.mapping_dict:
                mapped_symbols[symbol] = self.mapping_dict[symbol]
            else:
                invalid_symbols.append(symbol)

        return mapped_symbols, invalid_symbols

    def format_tv_output(self, mapped_symbols: Dict[str, str]) -> str:
        """Format the output in TradingView compatible format."""
        formatted_lines = []
        for symbol, industry in mapped_symbols.items():
            formatted_lines.append(f"{symbol}:{industry}")
        return "\n".join(formatted_lines)