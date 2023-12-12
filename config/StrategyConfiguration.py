
class TurtleATR:
    def __init__(self, strategy_json):
        turtle_atr_json = strategy_json['TurtleATR']
        self.atr_length = turtle_atr_json['atrLength']
        self.atr_avg_length = turtle_atr_json['atrAvgLength']
        self.body_length_constant = turtle_atr_json['bodyLengthConstant']
        self.basic_constant = turtle_atr_json['basicAtrConstant']
        self.bearish_constant = turtle_atr_json['bearishAtrConstant']
        self.risk_per_trade = turtle_atr_json['riskPerTrade']
        self.maLengths = turtle_atr_json['maLengths']
        self.higher_band_length = turtle_atr_json['higherBandLength']
        self.rsi_length = turtle_atr_json['rsiLength']
        self.rsi_low = turtle_atr_json['rsiLow']
        self.rsi_high = turtle_atr_json['rsiHigh']
        self.dividers = turtle_atr_json['dividers']
