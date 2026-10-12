import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet,
  TouchableOpacity, Alert, ActivityIndicator
} from 'react-native';
import { Calendar } from 'react-native-calendars';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Animatable from 'react-native-animatable';
import { getAvailableDates } from '../api/apiService';

export default function CalendarScreen({ navigation }) {
  const [markedDates, setMarkedDates] = useState({});
  const [userName, setUserName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    // Get user name
    const name = await AsyncStorage.getItem('userName');
    setUserName(name || 'User');

    try {
      const res = await getAvailableDates();
      const marks = {};
      res.data.dates.forEach(date => {
        marks[date] = {
          marked: true,
          dotColor: '#0D9488',
        };
      });
      setMarkedDates(marks);
    } catch (e) {
      // Fallback to known date if API fails
      setMarkedDates({
        '2025-04-10': { marked: true, dotColor: '#0D9488' },
      });
    } finally {
      setLoading(false);
    }
  };

  const onDayPress = (day) => {
    if (markedDates[day.dateString]) {
      navigation.navigate('Analytics', { date: day.dateString });
    } else {
      Alert.alert(
        'No Data',
        'No chair data available for this date yet.',
        [{ text: 'OK' }]
      );
    }
  };

  const logout = async () => {
    await AsyncStorage.clear();
    navigation.replace('Login');
  };

  return (
    <View style={styles.container}>

      {/* Header */}
      <Animatable.View animation="fadeInDown" duration={600} style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {userName} 👋</Text>
          <Text style={styles.subtitle}>Select a date to view your posture report</Text>
        </View>
        <TouchableOpacity onPress={logout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </Animatable.View>

      {/* Info Box */}
      <Animatable.View animation="fadeIn" delay={200} style={styles.infoBox}>
        <Text style={styles.infoText}>
          🟢  Dates with a green dot have data available
        </Text>
      </Animatable.View>

      {/* Calendar */}
      {loading ? (
        <ActivityIndicator size="large" color="#0D9488" style={{ marginTop: 40 }} />
      ) : (
        <Animatable.View animation="fadeInUp" delay={300} style={styles.calendarWrap}>
          <Calendar
            onDayPress={onDayPress}
            markedDates={markedDates}
            enableSwipeMonths={true}
            theme={{
              backgroundColor: '#0F172A',
              calendarBackground: '#1E293B',
              textSectionTitleColor: '#0D9488',
              selectedDayBackgroundColor: '#0D9488',
              selectedDayTextColor: '#ffffff',
              todayTextColor: '#0D9488',
              dayTextColor: '#E2E8F0',
              textDisabledColor: '#475569',
              dotColor: '#0D9488',
              selectedDotColor: '#ffffff',
              arrowColor: '#0D9488',
              monthTextColor: '#ffffff',
              textDayFontSize: 15,
              textMonthFontSize: 16,
              textDayHeaderFontSize: 13,
            }}
          />
        </Animatable.View>
      )}

      {/* Footer hint */}
      <Animatable.View animation="fadeIn" delay={500} style={styles.footer}>
        <Text style={styles.footerText}>
          📅  Data available for April 10, 2025
        </Text>
      </Animatable.View>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
    padding: 20,
    paddingTop: 60,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 20,
  },
  greeting: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    color: '#94A3B8',
    fontSize: 13,
    marginTop: 4,
  },
  logoutBtn: {
    backgroundColor: '#1E293B',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#F87171',
  },
  logoutText: {
    color: '#F87171',
    fontSize: 13,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#134E4A',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
  },
  infoText: {
    color: '#A7F3D0',
    fontSize: 13,
  },
  calendarWrap: {
    borderRadius: 20,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#1E293B',
  },
  footer: {
    marginTop: 20,
    alignItems: 'center',
  },
  footerText: {
    color: '#475569',
    fontSize: 13,
  },
});
