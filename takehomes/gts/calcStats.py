from collections import Counter, defaultdict
from csv import reader
from heapq import heappush, heappushpop
import argparse

class MedianFillSize:
    def __init__(self):
        self.small = []
        self.large = []

    def addFillSize(self, num):
        if len(self.small) == len(self.large):
            heappush(self.large, -heappushpop(self.small, -num))
        else:
            heappush(self.small, -heappushpop(self.large, num))

    def findMedian(self):
        if len(self.small) == len(self.large):
            return int(float(self.large[0] - self.small[0]) / 2.0)
        else:
            return int(float(self.large[0]))


def calcTradeStats(inputFile, outputFile):
    symbol_bought_dic = defaultdict(int)
    symbol_sold_dic = defaultdict(int)
    ex_bought = defaultdict(int)
    ex_sold = defaultdict(int)
    total_bought = 0
    total_sold = 0
    total_bought_notional = 0.0
    total_sold_notional = 0.0
    fill_size_sum, fill_idx = 0, 0
    median_finder = MedianFillSize()

    stdout_handle = open('stdout.txt', 'w')
    output_handle = open(outputFile, 'w')
    with open(inputFile, 'r') as f:
        csv_reader = reader(f)
        header = next(csv_reader)
        header.extend(['SymbolBought', 'SymbolSold', 'SymbolPosition',
                       'SymbolNotional', 'ExchangeBought', 'ExchangeSold', 'TotalBought',
                       'TotalSold', 'TotalBoughtNotional', 'TotalSoldNotional'])
        output_handle.write(','.join(header)+'\n')
        skipped_rows = []
        for row in csv_reader:
            try:
                row_4 = int(row[4])
                row_5 = float(row[5])
                fill_size_sum += row_4
                median_finder.addFillSize(row_4)
                fill_idx += 1
                exchange = row[-1]
                symbol = row[1]

                symbol_notional = row_4 * row_5

                if row[3] == 'b':
                    symbol_bought_dic[symbol] += row_4
                    ex_bought[exchange] += row_4
                    total_bought += row_4
                    total_bought_notional += symbol_notional
                else:
                    symbol_sold_dic[symbol] += row_4
                    ex_sold[exchange] += row_4
                    total_sold += row_4
                    total_sold_notional += symbol_notional

                symbol_position = symbol_bought_dic[symbol] - \
                    symbol_sold_dic[symbol]

                for _ in [symbol_bought_dic[symbol], symbol_sold_dic[symbol], symbol_position, symbol_notional, ex_bought[exchange], ex_sold[exchange],
                          total_bought, total_sold, total_bought_notional, total_sold_notional]:
                    row.append(str(_))

                output_handle.write(','.join(row)+'\n')
            except IndexError:  # skip row 301
                skipped_rows.append(fill_idx)

    output_handle.close()

    stdout_handle.write(f"Processed Trades: {fill_idx}\n\n")
    stdout_handle.write(f"Shares Bought: {total_bought}\n")
    stdout_handle.write(f"Shares Sold: {total_sold}\n")
    stdout_handle.write(f"Total Volume: {total_bought+total_sold}\n")
    stdout_handle.write(f"Notional Bought: ${total_bought_notional:.2f}\n")
    stdout_handle.write(f"Notional Sold: ${total_sold_notional:.2f}\n\n")

    ex_bought_sorted_key = sorted(dict(ex_bought))
    ex_sold_sorted_key = sorted(dict(ex_sold))

    stdout_handle.write('Per Exchange Volumes:\n')
    for k in ex_bought_sorted_key:
        stdout_handle.write(f"{k} Bought: {ex_bought[k]}\n")
        stdout_handle.write(f"{k} Sold: {ex_sold[k]}\n")

    stdout_handle.write(f"\nAverage Trade Size: {fill_size_sum / fill_idx:.2f}\n")
    stdout_handle.write(f"Median Trade Size: {median_finder.findMedian()}\n")
    active_symbol_string = []
    combined_dict = Counter(dict(symbol_bought_dic)) + \
        Counter(dict(symbol_sold_dic))
    for k in sorted(combined_dict, key=combined_dict.get, reverse=True):
        active_symbol_string.append(f"{k}({combined_dict[k]})")
        
    stdout_handle.write(f"\n10 Most Active Symbols: {','.join(active_symbol_string[:10])}\n\n")
    
    for skip in skipped_rows:
        stdout_handle.write(f"skipped row {skip} due to bad data quality")
    
    stdout_handle.close()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--inputFile",
    )
    parser.add_argument(
        "-o",
        "--outputFile",
    )
    
    args = parser.parse_args()
    
    calcTradeStats(args.inputFile, args.outputFile)