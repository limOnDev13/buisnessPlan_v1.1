import numpy as np
import matplotlib.pyplot as plt
import datetime as date


class DistributionParameters():
    # среднеквадратичное отклонение
    scale = 0
    # средний коэффициент массонакопления
    massAccumulationCoefficient = 0
    # количество рыб
    amountFishes = 0
    # массив значений, которые распределены по Гауссу в заданных параметрах
    _gaussValues = []

    def __init__(self, amountFishes,
                 scale=0.003,
                 massAccumulationCoefficientMin=0.07,
                 massAccumulationCoefficientMax=0.087):
        self.massAccumulationCoefficient = (massAccumulationCoefficientMin +
                                       massAccumulationCoefficientMax) / 2
        self.amountFishes = amountFishes
        self.scale = scale
        self._make_gaussian_distribution()

    def _make_gaussian_distribution(self):
        self._gaussValues = np.random.normal(self.massAccumulationCoefficient,
                                        self.scale,
                                        self.amountFishes)
        self._gaussValues.sort()

    def draw_hist_distribution(self, numberFishInOneColumn):
        plt.hist(self._gaussValues, numberFishInOneColumn)
        plt.show()

    def return_array_distributed_values(self):
        return self._gaussValues


class FishArrays():
    amountFishes = 0
    arrayFishes = []
    feedRatio = 1.5
    biomass = 0

    def __init__(self, feedRatio=1.5):
        self.feedRatio = feedRatio
        self.arrayFishes = list()

    def add_biomass(self, date, amountFishes, averageMass):
        # создаем параметры для нормального распределения коэффициентов массонакопления
        distributionParameters = DistributionParameters(amountFishes)
        arrayCoefficients = distributionParameters.return_array_distributed_values()

        # закидываем информацию о новой биомассе в массив
        for i in range(amountFishes):
            # ноль означает (количество дней в бассике, но это не точно
            # arrayFishes = [[startingDate, startingMass, massAccumulationCoefficient, currentMass],...]
            self.arrayFishes.append([date, averageMass, arrayCoefficients[i], averageMass])

        # увеличиваем количество рыбы в бассейне
        self.amountFishes += amountFishes
        self.biomass += amountFishes * averageMass / 1000

    def add_other_FishArrays(self, fishArrays):
        amountNewFishes = len(fishArrays)
        for i in range(amountNewFishes):
            self.biomass += fishArrays[i][3] / 1000
            self.arrayFishes.append(fishArrays[i])
        self.amountFishes += amountNewFishes

    def remove_biomass(self, amountIndexes, arrayIndexes):
        self.amountFishes -= amountIndexes
        removedFishes = list()
        for i in range(amountIndexes):
            fish = self.arrayFishes.pop(arrayIndexes[i])
            removedFishes.append(fish)
            self.biomass -= fish[2] / 1000
            # функция pop удаляет элемент и сдвигает все последующие элементы на 1,
            # значит все индексы нужно уменьшить на 1
            if (i != amountIndexes - 1):
                for j in range(i + 1, amountIndexes):
                    arrayIndexes[j] -= 1
        return removedFishes

    def update_biomass(self):
        self.biomass = 0
        for i in range(self.amountFishes):
            self.biomass += self.arrayFishes[i][3] / 1000


    def daily_work(self):
        # ежедневная масса корма
        dailyFeedMass = 0
        for i in range(self.amountFishes):
            previousMass = self.arrayFishes[i][3]
            # изменяем массу рыбки
            self._calculation_daily_growth(i)
            # расчитываем массу корма на сегодняшний день
            dailyFeedMass += self._determination_total_daily_weight_feed(previousMass, self.arrayFishes[i][3])

        # вернем массу корма
        return dailyFeedMass / 1000

    def _calculation_daily_growth(self, index):
        startingMass = self.arrayFishes[index][3]
        massAccumulationCoefficient = self.arrayFishes[index][2]
        newMass = (startingMass ** (1 / 3) +
                  massAccumulationCoefficient / 3) ** 3
        self.arrayFishes[index][3] = newMass
        self.biomass += (newMass - startingMass) / 1000

    # Проверено
    # функция, которая расчитывает ежедневную массу корма в зависимости от кормового коэффициента
    def _determination_total_daily_weight_feed(self, previousMass, currentMass):
        relativeGrowth = (currentMass - previousMass) / previousMass
        result = previousMass * relativeGrowth * self.feedRatio
        return result

    def get_biomass(self):
        return self.biomass

    def get_FishArrays(self):
        return self.arrayFishes

    def calculate_average_mass(self):
        averageMass = 0
        for i in range(self.amountFishes):
            averageMass += self.arrayFishes[i][3]

        averageMass /= self.amountFishes
        return averageMass


class Pool():
    square = 0
    limitsPlantingDensity = [0, 0]
    arrayFishes = 0
    # количество мальков в 1 упаковке
    singleVolumeFish = 0
    # цена на мальков
    costFishFry = [[5, 35],
                   [10, 40],
                   [20, 45],
                   [30, 50],
                   [50, 60],
                   [100, 130]]
    # массив, в котором хранится информация о покупке мальков
    arrayFryPurchases = list()
    # текущая плотность посадки
    currentDensity = 0
    # есть переизбыток мальков?
    isThereOverabundanceFish = False
    # массив кормежек
    feeding = list()
    # масса товарной рыбы
    massComercialFish = 350

    def __init__(self, square, singleVolumeFish=100, massComercialFish=350,
                 minimumPlantingDensity=20, maximumPlantingDensity=40):
        self.square = square
        self.massComercialFish = massComercialFish
        self.limitsPlantingDensity[0], self.limitsPlantingDensity[1] = \
            minimumPlantingDensity, maximumPlantingDensity
        self.singleVolumeFish = singleVolumeFish
        self.arrayFishes = FishArrays()
        self.feeding = list()
        self.arrayFryPurchases = list()

    def add_new_biomass(self, amountFishes, averageMass, date):
        self.arrayFishes.add_biomass(date, amountFishes, averageMass)
        # сохраним инфо о покупки мальков
        # arrayFryPurchases[i] = [date, amountFries, averageMass, totalPrice]
        totalPrice = 0
        for i in range(len(self.costFishFry)):
            if (averageMass < self.costFishFry[i][0]):
                totalPrice = amountFishes * self.costFishFry[i][1]
        self.arrayFryPurchases.append([date, amountFishes, averageMass, totalPrice])
        self.currentDensity = amountFishes * (averageMass / 1000) / self.square

    def daily_growth(self, day):
        todayFeedMass = self.arrayFishes.daily_work()
        # сохраняем массы кормежек
        self.feeding.append([day, todayFeedMass])

        # проверяем, есть ли переизбыток
        self.currentDensity = self.arrayFishes.biomass / self.square
        if (self.currentDensity >= self.limitsPlantingDensity[1]):
            self.isThereOverabundanceFish = True
        else:
            self.isThereOverabundanceFish = False

    # функция будет возвращать, выросло ли достаточно рыбы на продажу
    def has_there_been_enough_fish_sale(self):
        numberGrowthFish = 0
        for i in range(self.arrayFishes.amountFishes):
            if (self.arrayFishes.arrayFishes[i][3] > self.massComercialFish):
                numberGrowthFish += 1

        if ((numberGrowthFish >= self.singleVolumeFish) or
                (numberGrowthFish == self.arrayFishes.amountFishes)):
            self.arrayFishes.arrayFishes.sort(key=lambda x: x[3])
            result = numberGrowthFish
        else:
            result = 0

        return result

    def calculate_when_fish_will_grow_up(self, numberFishForSale, startDate):
        amountGrowthFish = 0
        day = startDate
        # копируем массив рыб
        testFishes = FishArrays()
        copiedArrayFish = list()
        # arrayFishes = [[startingDate, startingMass, massAccumulationCoefficient, currentMass],...]
        for i in range(self.arrayFishes.amountFishes):
            startingDate = self.arrayFishes.arrayFishes[i][0]
            startingMass = self.arrayFishes.arrayFishes[i][1]
            massAccumulationCoefficient = self.arrayFishes.arrayFishes[i][2]
            currentMass = self.arrayFishes.arrayFishes[i][3]
            copiedArrayFish.append([startingDate, startingMass, massAccumulationCoefficient, currentMass])
        testFishes.add_other_FishArrays(copiedArrayFish)

        while ((amountGrowthFish < numberFishForSale) and
               (amountGrowthFish != testFishes.amountFishes)):
            amountGrowthFish = 0
            testFishes.daily_work()
            x = testFishes.arrayFishes[0][3]
            for i in range(testFishes.amountFishes):
                if (testFishes.arrayFishes[i][3] >= self.massComercialFish):
                    amountGrowthFish += 1
            day += date.timedelta(1)
            testDensity = testFishes.biomass / self.square

        return [day, (day - startDate).days,  (day - startDate).days / 30, amountGrowthFish, testDensity]

    def calculate_density(self, fishArray):
        mass = 0
        for i in range(len(fishArray)):
            mass += fishArray[i][3] / 1000

        return mass / self.square

    def update_density(self):
        self.currentDensity = self.arrayFishes.biomass / self.square

    # функция рассчитывает, когда (и через сколько дней) плотность посадки дойдет до лимита
    def calculate_when_density_exceeds_limit(self, startDay):
        # копируем массив рыбок
        testArrayFishes = FishArrays()
        testArray = list()

        for i in range(self.arrayFishes.amountFishes):
            # arrayFishes = [[startingDate, startingMass, massAccumulationCoefficient, currentMass],...]
            x = list()
            for j in range(4):
                x.append(self.arrayFishes.arrayFishes[i][j])
            testArray.append(x)

        testArrayFishes.add_other_FishArrays(testArray)
        density = self.currentDensity

        day = startDay
        while(density < self.limitsPlantingDensity[1]):
            testArrayFishes.daily_work()
            density = self.calculate_density(testArrayFishes.arrayFishes)
            day += date.timedelta(1)

        averageMass = testArrayFishes.calculate_average_mass()

        return [day, (day - startDay).days, (day - startDay).days / 30, averageMass]

    def determine_indices_largest_fish(self, amountFishesToRemove):
        self.arrayFishes.arrayFishes.sort(key=lambda x: x[3])
        indeces = list()
        for i in range(self.arrayFishes.amountFishes - amountFishesToRemove,
                       self.arrayFishes.amountFishes):
            indeces.append(i)

        return indeces


class CWSD():
    amountPools = 0
    amountGroups = 0
    # температура воды
    temperature = 21
    # арендная плата
    rent = 70000
    # стоимость киловатт в час
    costElectricityPerHour = 3.17
    # мощность узв
    equipmentCapacity = 5.6
    # стоимость корма
    feedPrice = 260
    onePoolSquare = 0
    pools = list()
    fishPrice = 1000
    profit = list()

    def __init__(self, poolSquare, amountPools=8, amountGroups=4, fishPrice=1000,
                 feedPrice=260, equipmentCapacity=5.5, rent=70000,
                 costElectricityPerHour=3.17, temperature=21):
        self.onePoolSquare = poolSquare
        self.amountGroups = amountGroups
        self.amountPools = amountPools
        self.fishPrice = fishPrice
        self.temperature = temperature
        self.rent = rent
        self.costElectricityPerHour = costElectricityPerHour
        self.equipmentCapacity = equipmentCapacity
        self.feedPrice = feedPrice
        self.pools = list()
        self.profit = list()

        for i in range(amountPools):
            pool = Pool(poolSquare)
            self.pools.append(pool)

    def add_biomass_in_pool(self, poolNumber, amountFishes, mass, date):
        self.pools[poolNumber].add_new_biomass(amountFishes, mass, date)

    # функция для расчета технических расходов (электричество, тепло и т.д.)
    def _calculate_technical_costs(self, startingDate, endingDate):
        deltaTime = endingDate - startingDate
        amountDays = deltaTime.days
        electrisityCost = amountDays * 24 * self.equipmentCapacity * self.costElectricityPerHour
        rentCost = (int(amountDays / 30)) * self.rent
        return [rentCost, electrisityCost, rentCost + electrisityCost]

    def _calculate_biological_costs(self, startingDate, endingDate):
        day = startingDate
        feedMass = 0
        fryCost = 0

        while(day < endingDate):
            for i in range(self.amountGroups):
                # подсчет затрат на корма
                startingDayInThisPool = self.pools[i].feeding[0][0]
                if (day >= startingDayInThisPool):
                    amountDaysFeedingInThisPool = (day - startingDayInThisPool).days
                    feedMass += self.pools[i].feeding[amountDaysFeedingInThisPool][1]

                # подсчет затрат на мальков.
                for j in range(len(self.pools[i].arrayFryPurchases)):
                    if (day == self.pools[i].arrayFryPurchases[j][0]):
                        fryCost += self.pools[i].arrayFryPurchases[j][3]
                    elif (day > self.pools[i].arrayFryPurchases[j][0]):
                        break
            day += date.timedelta(1)

        feedCost = feedMass * self.feedPrice
        return [feedCost, fryCost, feedCost + fryCost]

    def calculate_profit(self, startingDate, endingDate):
        expenses1 = self._calculate_biological_costs(startingDate, endingDate)
        expenses2 = self._calculate_technical_costs(startingDate, endingDate)
        expenses = expenses1[2] + expenses2[2]

        profit = 0
        for i in range(len(self.profit)):
            profit += self.profit[i][3]

        return [profit, expenses, profit - expenses]

    def __calculate_when_fish_will_grow_up(self):
        mass = [20, 50, 70, 100]
        amountFishes = 1000
        amountFishesInOnePackage = 100
        for i in range(4):
            self.pools[i].add_new_biomass(amountFishes, mass[i], date.date.today())
            print(self.pools[i].calculate_when_fish_will_grow_up(amountFishesInOnePackage, date.date.today()))

    def optimize_first_fry_in_comercial_pool(self, startAmount,
                                             step, mass, limitDensity,
                                             numberFishForSale):
        amount = startAmount
        density = 0
        result = 0
        while (density < limitDensity):
            pool = Pool(self.onePoolSquare)
            pool.add_new_biomass(amount, mass, date.date.today())
            # [day, (day - startDate).days,  (day - startDate).days / 30, amountGrowthFish, testDensity]
            x = pool.calculate_when_fish_will_grow_up(numberFishForSale, date.date.today())
            density = x[4]
            result = [amount, x[1]]
            amount += step

        # возвращаем количество мальков и количество дней, которые они будут расти
        return result

    def move_fish_from_one_pool_to_another(self, numberOnePool,
                                           numberAnotherPool, amountFishForMoving):
        indeces = self.pools[numberOnePool].determine_indices_largest_fish(amountFishForMoving)
        removedFishes = self.pools[numberOnePool].arrayFishes.remove_biomass(len(indeces), indeces)
        self.pools[numberAnotherPool].arrayFishes.add_other_FishArrays(removedFishes)
        self.pools[numberOnePool].update_density()
        self.pools[numberAnotherPool].update_density()


    def print_number_fish_in_each_pool(self):
        for i in range(self.amountGroups):
            print(self.pools[i].arrayFishes.amountFishes)

    def print_array_fishes_in_each_pool(self):
        for i in range(self.amountGroups):
            print(self.pools[i].arrayFishes.arrayFishes)

    def daily_work_CWSD(self, day, minimumFishForMove):
        # сделаем ежедневный рост каждой рыбки
        for i in range(self.amountPools):
            self.pools[i].daily_growth(day)

        # заглянем в каждый бассейн и если в каком-нибудь
        # плотность превышает допустимое значение, то перекинем пакет рыбок в следующий бассейн
        for i in range(self.amountPools - 1):
            while (self.pools[i].arrayFishes.biomass / self.pools[i].square >= self.pools[i].limitsPlantingDensity[1]):
                x = min(minimumFishForMove, self.pools[i].arrayFishes.amountFishes)
                self.move_fish_from_one_pool_to_another(i, i + 1, x)
                self.pools[i].update_density()
                self.pools[i + 1].update_density()
                self.pools[i].arrayFishes.update_biomass()
                self.pools[i + 1].arrayFishes.update_biomass()

        # заглянем во все бассейны, и если там есть, что продать, то продаем
        self.sell_fish_in_pool(day)

        # так как всю лишнюю рыбу скидываем в следующий бассейн,
        # то после всех операций перебор с рыбой может быть только в последнем бассейне
        if (self.pools[self.amountPools - 1].currentDensity >=
                self.pools[self.amountPools - 1].limitsPlantingDensity[1]):
            return True

        return False

    def calculate_number_fish_that_will_reach_density_limit_in_time(self, days, startAmount,
                                                                    step, mass, limitDansity, startDay):
        curentDensity = 0
        amount = startAmount
        result = 0
        while (curentDensity < limitDansity):
            day = startDay
            testPool = Pool(self.onePoolSquare)
            testPool.add_new_biomass(amount, mass, startDay)
            while (day < startDay + date.timedelta(days)):
                testPool.daily_growth(day)
                day += date.timedelta(1)
            curentDensity = testPool.calculate_density(testPool.arrayFishes.arrayFishes)
            result = amount
            amount += step

        return result

    def first_stocking_entire_CWSD1(self, sellDays, masses, deltaAmount):
        # список количеств рыбы для каждой массы
        numbers = list()
        # рассчитаем количество рыбы для товарного басса (он идет с индексом 0)
        # [amount, (day - startDate).days]
        optimazedComPool = self.optimize_first_fry_in_comercial_pool(50, 50, masses[0], 40, 100)
        # время до первой продажи
        growthTime = optimazedComPool[1] + sellDays
        # количество мальков в товарном бассе
        amountFishInComPool = optimazedComPool[0]
        numbers.append(amountFishInComPool - deltaAmount)
        # теперь рассчитаем количество мальков для каждого басса, чтобы во всех
        # бассах к этому времени
        for i in range(1, self.amountGroups):
            x = self.calculate_number_fish_that_will_reach_density_limit_in_time(growthTime, 50, 50,
                                                                             masses[i], 40, date.date.today())
            numbers.append(x)

        result = list()
        for i in range(self.amountGroups):
            result.append([masses[i], numbers[i]])

        return result

    def sell_fish_in_pool(self, date):
        for i in range(self.amountPools):
            amountGrowthFish = self.pools[i].has_there_been_enough_fish_sale()
            if (amountGrowthFish > 0):
                indeces = self.pools[i].determine_indices_largest_fish(amountGrowthFish)
                soldFishes = self.pools[i].arrayFishes.remove_biomass(amountGrowthFish, indeces)
                self.pools[i].update_density()

                totalSoldBiomass = 0
                for i in range(amountGrowthFish):
                    totalSoldBiomass += soldFishes[i][3] / 1000

                self.profit.append([date, amountGrowthFish, totalSoldBiomass, totalSoldBiomass * self.fishPrice])

    def clear_CWSD(self):
        self.pools = list()
        for i in range(self.amountPools):
            newPool = Pool(self.onePoolSquare)
            self.pools.append(newPool)

        self.profit = list()
        self.expenses = list()

    def return_amount_fish(self):
        result = 0
        for i in range(self.amountPools):
            result += self.pools[i].arrayFishes.amountFishes
        return result

    def print_info(self):
        for i in range(self.amountPools):
            print(self.pools[i].arrayFishes.amountFishes)
            print(self.pools[i].arrayFishes.arrayFishes)
        print('_______________________________________________')


class Optimiztion():
    def _create_result(self, arr1, arr2, profit):
        result = list()
        for i in range(len(arr1)):
            x = [arr1[i], arr2[i]]
            result.append(x)
        result.append(profit)
        return result

    def _calculate_amount_operations(self, amountGroups, start, end, step):
        result = 0
        x = start
        while (x < end):
            x += step
            result += 1
        result = int(result ** amountGroups)
        return result

    def _show_calculations(self, currentAmountOperations, totalAmountOperations):
        procent = int(currentAmountOperations / totalAmountOperations * 100)
        z = ''
        if (currentAmountOperations % 3 == 0):
            z += '|'
        elif (currentAmountOperations % 3 == 1):
            z += '/'
        else:
            z += '-'

        x = procent // 5
        result = ''
        for i in range(x):
            result += '#'
        for i in range(x, 20):
            result += '.'
        result += z
        print(procent, '% ', result)

    def first_stocking_entire_CWSD2(self, masses, step=50, amountGroups=4,
                                    amountPools=8, square=5, maxDensity=40, massCommercialFish=0.35):
        x = CWSD(square, amountPools, amountGroups)
        # список количеств рыбы для каждой массы
        startNumber = int(((square * maxDensity / massCommercialFish) // 10) * 10)

        # будем варьировать
        # максимальное число - это количество товарной рыбы во всех бассейнах
        # endNumber = int(x.amountPools * x.onePoolSquare * maxDensity * massCommercialFish)
        endNumber = 1500
        numbs = [startNumber, startNumber, startNumber, startNumber]
        maxProfit = 0

        result = []

        # поссчитаем количество бассейнов, в которых мальки одной группы
        koef = int(x.amountPools / x.amountGroups)

        # нужно следить, чтобы циклы работали
        totalAmountOperations = self._calculate_amount_operations(amountGroups, startNumber, endNumber, step)
        currentAmountOperations = 0
        # единичный цикл
        # добавляем биомассу
        while (numbs[0] < endNumber):
            numbs[1] = startNumber
            while (numbs[1] < endNumber):
                numbs[2] = startNumber
                while (numbs[2] < endNumber):
                    numbs[3] = startNumber
                    while (numbs[3] < endNumber):
                        x = CWSD(5, amountPools, amountGroups)
                        for i in range(4):
                            for j in range(koef):
                                x.add_biomass_in_pool(i * 2 + j, numbs[i], masses[i], date.date.today())

                        # flag будет говорить - превысили ли мы плотность посадки во всем узв
                        flag = False
                        day = date.date.today()
                        # выход из цикла - либо превышение лимита плотности во всем узв, либо продажа всей рыбы
                        while ((not flag) and (x.return_amount_fish() != 0)):
                            flag = x.daily_work_CWSD(day, 100)
                            day += date.timedelta(1)
                        # если не превысили, значит все ок, посчитаем выручку и расходы
                        if (not flag):
                            currentProfit = x.calculate_profit(date.date.today(), day)

                            # если чистая прибыль выше предыдущих итераций, то ставим новый результат
                            if (maxProfit < currentProfit[2]):
                                result = self._create_result(numbs, masses, currentProfit[2])
                                maxProfit = currentProfit[2]
                        numbs[3] += step
                        currentAmountOperations += 1
                        self._show_calculations(currentAmountOperations, totalAmountOperations)
                    numbs[2] += step
                numbs[1] += step
            numbs[0] += step

        print('После продажи, будут такие плотности:')
        for i in range(x.amountPools):
            print(i, ' ', x.pools[i].arrayFishes.calculate_average_mass(), x.pools[i].arrayFishes.amountFishes, x.pools[i].currentDensity)
        return result


x = Optimiztion()
masses = [20, 50, 70, 100]
result = x.first_stocking_entire_CWSD2(masses, 100)
print('Лучший результат: ', result)
