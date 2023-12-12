from util.FileUtil import FileUtil
from config.StrategyConfiguration import TurtleATR

if __name__ == '__main__':
    json = FileUtil.load_strategy_config("sample/strategy.json")
    turtle_atr = TurtleATR(json)
    print(turtle_atr.rsi_high)