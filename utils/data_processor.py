import pandas as pd
from typing import List, Tuple, Dict

class IndustryMapper:
    def __init__(self):
        """Initialize the mapper with the permanent backend database."""
        try:
            self.load_database()
        except Exception as e:
            raise Exception(f"Failed to load industry mapping database: {str(e)}")

    def load_database(self):
        """Load the permanent industry mapping database."""
        try:
            self.mapping_df = pd.read_csv('data/industry_mapping.csv')
            self.mapping_dict = dict(zip(
                self.mapping_df['symbol'].str.upper(),
                self.mapping_df['industry']
            ))
        except FileNotFoundError:
            raise Exception("Industry mapping database not found")
        except Exception as e:
            raise Exception(f"Error reading industry database: {str(e)}")

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

    def get_available_industries(self) -> List[str]:
        """Get list of all available industries in the database."""
        return sorted(self.mapping_df['industry'].unique())

    def get_database_stats(self) -> Dict[str, int]:
        """Get statistics about the mapping database."""
        return {
            'total_symbols': len(self.mapping_df),
            'total_industries': len(self.get_available_industries())
        }