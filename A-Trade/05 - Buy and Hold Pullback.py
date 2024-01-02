from datetime import datetime
import backtrader as bt
import matplotlib.pyplot as plt

class BuyAndHoldPullback(bt.Strategy):
    """Покупка и удержание на откате"""

    def log(self, txt, dt=None):
        """Вывод строки с датой на консоль"""
        dt = bt.num2date(self.datas[0].datetime[0]).date() if dt is None else dt  # Заданная дата или дата текущего бара
        print(f'{dt.strftime("%d.%m.%Y")}, {txt}')  # Выводим дату с заданным текстом на консоль

    def __init__(self):
        """Инициализация торговой системы"""
        self.DataClose = self.datas[0].close

    def next(self):
        """Получение следующего бара"""
        self.log(f'Close={self.DataClose[0]:.2f}')
        isSignalBuy = self.DataClose[0] < self.DataClose[-1] < self.DataClose[-2]  # Цена падает 2 сессии подряд
        if isSignalBuy:  # Если пришла заявка на покупку
            self.log('Buy Market')
            self.buy()  # Заявка на покупку одной акции по рыночной цене


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    cerebro = bt.Cerebro()  # Инициируем "движок" BackTrader
    cerebro.addstrategy(BuyAndHoldPullback)  # Привязываем торговую систему
    data = bt.feeds.GenericCSVData(
        # Можно принимать любые CSV файлы с разделителем десятичных знаков в виде точки https://backtrader.com/docu/datafeed-develop-csv/
        dataname='Data/TQBR.SBER_D1.txt',  # Файл для импорта
        separator='\t',  # Колонки разделены табуляцией
        dtformat='%d.%m.%Y %H:%M',  # Формат даты/времени DD.MM.YYYY HH:MI
        openinterest=-1,  # Открытого интереса в файле нет
        fromdate=datetime(2019, 1, 1),  # Начальная дата приема исторических данных (Входит)
        todate=datetime(2024, 1, 1))  # Конечная дата приема исторических данных (Не входит)
    cerebro.adddata(data)  # Привязываем исторические данные
    cerebro.broker.setcash(1000000)  # Стартовый капитал для "бумажной" торговли
    print(f'Старовый капитал: {cerebro.broker.getvalue():.2f}')
    cerebro.run()  # Запуск торговой системы
    print(f'Конечный капитал: {cerebro.broker.getvalue():.2f}')
    cerebro.plot()  # Рисуем график

