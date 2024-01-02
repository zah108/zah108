from datetime import datetime
import backtrader as bt


class PriceMACross(bt.Strategy):
    """Пересечение цены и SMA"""
    params = (  # Параметры торговой системы
        ('SMAPeriod', 26),  # Период SMA
    )

    def log(self, txt, dt=None):
        """Вывод строки с датой на консоль"""
        dt = bt.num2date(self.datas[0].datetime[0]) if dt is None else dt  # Заданная дата или дата текущего бара
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Выводим дату и время с заданным текстом на консоль

    def __init__(self):
        """Инициализация торговой системы"""
        self.close = self.datas[0].close  # Цены закрытия
        self.order = None  # Заявка
        self.sma = bt.indicators.SMA(self.datas[0], period=self.p.SMAPeriod)  # SMA

    def notify_order(self, order):
        """Изменение статуса заявки"""
        if order.status in [order.Submitted, order.Accepted]:  # Если заявка не исполнена (отправлена брокеру или принята брокером)
            return  # то статус заявки не изменился, выходим, дальше не продолжаем

        if order.status in [order.Completed]:  # Если заявка исполнена
            if order.isbuy():  # Заявка на покупку
                self.log(f'Bought @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
            elif order.issell():  # Заявка на продажу
                self.log(f'Sold @{order.executed.price:.2f}, Cost={order.executed.value:.2f}, Comm={order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:  # Заявка отменена, нет средств, отклонена брокером
            self.log('Canceled/Margin/Rejected')
        self.order = None  # Этой заявки больше нет


    def notify_trade(self, trade):
        """Изменение статуса позиции"""
        if not trade.isclosed:  # Если позиция не закрыта
            return  # то статус позиции не изменился, выходим, дальше не продолжаем

        self.log(f'Trade Profit, Gross={trade.pnl:.2f}, NET={trade.pnlcomm:.2f}')
    
    def next(self):
        """Получение следующего бара"""
        self.log(f'Close={self.close[0]:.2f}')
        if self.order:  # Если есть неисполненная заявка
            return  # то выходим, дальше не продолжаем
        
        if not self.position:  # Если позиции нет
            isSignalBuy = self.close[0] > self.sma[0]  # Цена закрылась выше скользящей
            if isSignalBuy:  # Если пришла заявка на покупку
                self.log('Buy Market')
                self.order = self.buy()  # Заявка на покупку по рыночной цене
        else:  # Если позиция есть
            isSignalSell = self.close[0] < self.sma[0]  # Цена закрылась ниже скользящей
            if isSignalSell:  # Если пришла заявка на продажу
                self.log('Sell Market')
                self.order = self.sell()  # Заявка на продажу по рыночной цене


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro()  # Инициируем "движок" BT
    cerebro.addstrategy(PriceMACross, SMAPeriod=26)  # Привязываем торговую систему с параметрами
    data = bt.feeds.GenericCSVData(
        # Можно принимать любые CSV файлы с разделителем десятичных знаков в виде точки https://backtrader.com/docu/datafeed-develop-csv/
        dataname='Data/TQBR.SBER_D1.txt',  # Файл для импорта
        separator='\t',  # Колонки разделены табуляцией
        dtformat='%d.%m.%Y %H:%M',  # Формат даты/времени DD.MM.YYYY HH:MI
        # dtformat='%d.%m.%Y',  # Формат даты/времени DD.MM.YYYY HH:MI
        openinterest=-1,  # Открытого интереса в файле нет
        fromdate=datetime(2019, 1, 1),  # Начальная дата приема исторических данных (Входит)
        todate=datetime(2021, 1, 1))  # Конечная дата приема исторических данных (Не входит)
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(1000000)  # Стартовый капитал для "бумажной" торговли
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)  # Кол-во акций для покупки/продажи
    # cerebro.broker.setcommission(commission=0.001)  # Комиссия брокера 0.1% от суммы каждой исполненной заявки
    # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')  # Привязываем анализатор закрытых сделок
    brokerStartValue = cerebro.broker.getvalue()  # Стартовый капитал
    print(f'Стартовый капитал: {brokerStartValue:.2f}')
    result = cerebro.run()  # Запуск торговой системы
    # brokerFinalValue = cerebro.broker.getvalue()  # Конечный капитал
    # print(f'Конечный капитал: {brokerFinalValue:.2f}')
    # print(f'Прибыль/убытки с комиссией: {(brokerFinalValue - brokerStartValue):.2f}')
    # analysis = result[0].analyzers.TradeAnalyzer.get_analysis()  # Получаем данные анализатора закрытых сделок
    # print('Прибыль/убытки по закрытым сделкам:')
    # print(f'- Без комиссии {analysis["pnl"]["gross"]["total"]:.2f}')
    # print(f'- С комиссией  {analysis["pnl"]["net"]["total"]:.2f}')
    cerebro.plot()  # Рисуем график
