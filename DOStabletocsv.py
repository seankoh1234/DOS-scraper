from gettable import combineCSV

tabletitles=dict(zip(
    ["M015721","M015731","M015661", 
     "M015651", 
    "M015751", "M015681", "M015741", 
    "M015771", "M015761", "M015811", 
    "M015691", "M015801", "M015851", "M015871", 
    "M183901", "M183891", "M183741", 
    "M700851", "M700051", "M700041"],
    ['Real GDP Annual (DOS)','Nominal GDP Annual (DOS)','Real GDP Quarterly (DOS)','Nominal GDP Quarterly (DOS)',
    'Deflator Annual (DOS)','Deflator Quarterly (DOS)','Contribution to Growth (DOS)',
    'Real VAP Change','Real VAP Annual (DOS)','Current VAP Annual (DOS)',
    'Real VAP Quarterly (DOS)','Current VAP Quarterly (DOS)','VA per Actual Hr (DOS)','Real VA per Actual Hr (Qtr)',
    'Changes in Emp (Annual) (DOS)','Changes in Emp (Qtr) (DOS)', 'Unit Labour Cost Index (DOS)',
    'Exchange Rates, Avg, Annual','Exchange Rates, Avg, Monthly','Exchange, End of Period, Mthly']))

combineCSV(tabletitles, 'DOS_data.xlsx')