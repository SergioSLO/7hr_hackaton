import React, { useEffect, useState, useMemo } from 'react';
import { StyleSheet, View, TouchableOpacity, FlatList, Text, Dimensions } from 'react-native';
import { BarChart } from 'react-native-chart-kit';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { fetchTransactions } from '@/services/api';

interface Transaction {
  tipo: string;
  monto: number;
  categoria: string;
  fecha: string;
  descripcion: string;
}

export default function DatosScreen() {
  const [weekOffset, setWeekOffset] = useState(0); // 0 = current week
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const weekStartDate = useMemo(() => {
    const now = new Date();
    const monday = new Date(now);
    const day = now.getDay();
    const diff = (day === 0 ? -6 : 1) - day; // Monday as start of week
    monday.setDate(now.getDate() + diff + weekOffset * 7);
    monday.setHours(0, 0, 0, 0);
    return monday;
  }, [weekOffset]);

  useEffect(() => {
    const start = weekStartDate.toISOString().slice(0, 10);
    fetchTransactions(start)
      .then(setTransactions)
      .catch((err) => console.error(err));
  }, [weekStartDate]);

  const totals = useMemo(() => {
    const arr = Array(7).fill(0);
    transactions.forEach((t) => {
      const d = new Date(t.fecha);
      const idx = (d.getDay() + 6) % 7; // Monday=0
      const sign = t.tipo === 'egreso' ? -1 : 1;
      arr[idx] += sign * t.monto;
    });
    return arr;
  }, [transactions]);

  const weekLabel = useMemo(() => {
    const end = new Date(weekStartDate);
    end.setDate(end.getDate() + 6);
    return `${weekStartDate.toLocaleDateString()} - ${end.toLocaleDateString()}`;
  }, [weekStartDate]);

  const chartData = {
    labels: ['L', 'M', 'M', 'J', 'V', 'S', 'D'],
    datasets: [{ data: totals }],
  };

  return (
    <ThemedView style={styles.container}>
      <ThemedText type="title" style={styles.title}>Datos</ThemedText>
      <BarChart
        data={chartData}
        width={Dimensions.get('window').width - 32}
        height={220}
        fromZero
        showValuesOnTopOfBars
        chartConfig={{
          backgroundColor: '#ffffff',
          backgroundGradientFrom: '#ffffff',
          backgroundGradientTo: '#ffffff',
          decimalPlaces: 2,
          color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
        }}
        style={styles.chart}
      />
      <View style={styles.pagination}>
        <TouchableOpacity onPress={() => setWeekOffset((o) => o - 1)}>
          <Text style={styles.link}>Anterior</Text>
        </TouchableOpacity>
        <ThemedText>{weekLabel}</ThemedText>
        <TouchableOpacity onPress={() => setWeekOffset((o) => o + 1)}>
          <Text style={styles.link}>Siguiente</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={transactions}
        keyExtractor={(_, i) => i.toString()}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text style={[styles.cell, { flex: 2 }]}>{item.fecha}</Text>
            <Text style={[styles.cell, { flex: 2 }]}>{item.categoria}</Text>
            <Text style={[styles.cell, { flex: 3 }]}>{item.descripcion}</Text>
            <Text style={[styles.cell, { flex: 1, textAlign: 'right' }]}>
              {item.monto.toFixed(2)}
            </Text>
          </View>
        )}
        ListHeaderComponent={() => (
          <View style={[styles.row, styles.headerRow]}>
            <Text style={[styles.cell, { flex: 2 }]}>Fecha</Text>
            <Text style={[styles.cell, { flex: 2 }]}>Categoría</Text>
            <Text style={[styles.cell, { flex: 3 }]}>Descripción</Text>
            <Text style={[styles.cell, { flex: 1, textAlign: 'right' }]}>Monto</Text>
          </View>
        )}
      />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    textAlign: 'center',
    marginBottom: 16,
  },
  chart: {
    marginVertical: 8,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  link: {
    color: '#007AFF',
  },
  row: {
    flexDirection: 'row',
    paddingVertical: 8,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: '#ccc',
  },
  headerRow: {
    backgroundColor: '#eee',
  },
  cell: {
    paddingHorizontal: 4,
    fontSize: 12,
  },
});
