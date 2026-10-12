import React, { useEffect, useState } from 'react';
import {
  View, Text, ScrollView, StyleSheet,
  ActivityIndicator, TouchableOpacity
} from 'react-native';
import * as Animatable from 'react-native-animatable';
import { LinearGradient } from 'expo-linear-gradient';
import { getAnalytics } from '../api/apiService';
import PostureAnimation from '../components/PostureAnimation';

export default function AnalyticsScreen({ route, navigation }) {
  const { date } = route.params;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await getAnalytics(date);
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#0D9488" />
        <Text style={styles.loadingText}>Loading your report...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorEmoji}>😕</Text>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backBtnText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const score = data.posture_score;
  const scoreColor = score >= 70 ? '#10B981' : score < 40 ? '#EF4444' : '#F59E0B';
  const totalPosture = Object.values(data.posture_counts).reduce((a, b) => a + b, 0);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>

      {/* Hero Header */}
      <LinearGradient colors={['#0D9488', '#0F172A']} style={styles.hero}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backArrow}>
          <Text style={styles.backArrowText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.dateLabel}>{date}</Text>
        <Text style={styles.heroTitle}>Posture Report</Text>
        <Animatable.Text
          animation="bounceIn"
          delay={300}
          style={[styles.scoreText, { color: scoreColor }]}
        >
          {score}%
        </Animatable.Text>
        <Text style={styles.scoreLabel}>Overall Posture Score</Text>
      </LinearGradient>

      <View style={styles.body}>

        {/* Posture Animation */}
        <Animatable.View animation="fadeInUp" delay={200}>
          <PostureAnimation score={score} />
        </Animatable.View>

        {/* Stats Row */}
        <Animatable.View animation="fadeInUp" delay={300} style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>⏱️</Text>
            <Text style={styles.statValue}>{data.total_sitting_minutes}</Text>
            <Text style={styles.statLabel}>Mins Sitting</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>🌡️</Text>
            <Text style={styles.statValue}>{data.avg_temperature}°</Text>
            <Text style={styles.statLabel}>Avg Temp</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>📊</Text>
            <Text style={styles.statValue}>{data.total_readings}</Text>
            <Text style={styles.statLabel}>Readings</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>🔔</Text>
            <Text style={styles.statValue}>{data.alerts_sent}</Text>
            <Text style={styles.statLabel}>Alerts</Text>
          </View>
        </Animatable.View>

        {/* Posture Breakdown */}
        <Animatable.View animation="fadeInUp" delay={400} style={styles.section}>
          <Text style={styles.sectionTitle}>📈 Posture Breakdown</Text>
          {Object.entries(data.posture_counts).map(([label, count], index) => {
            const pct = Math.round((count / totalPosture) * 100);
            const color = label === 'Good' ? '#10B981' : label === 'Bad' ? '#EF4444' : '#F59E0B';
            const displayLabel = label;
            return (
              <Animatable.View
                key={label}
                animation="fadeInLeft"
                delay={500 + index * 100}
                style={styles.barWrap}
              >
                <Text style={styles.barLabel}>{displayLabel}</Text>
                <View style={styles.barBg}>
                  <Animatable.View
                    animation="slideInLeft"
                    delay={600 + index * 100}
                    duration={800}
                    style={[
                      styles.barFill,
                      { width: `${pct}%`, backgroundColor: color }
                    ]}
                  />
                </View>
                <Text style={styles.barPct}>{pct}%</Text>
              </Animatable.View>
            );
          })}
        </Animatable.View>

        {/* Temperature Stats */}
        <Animatable.View animation="fadeInUp" delay={500} style={styles.section}>
          <Text style={styles.sectionTitle}>🌡️ Temperature Details</Text>
          <View style={styles.tempRow}>
            <View style={styles.tempCard}>
              <Text style={styles.tempValue}>{data.min_temperature}°C</Text>
              <Text style={styles.tempLabel}>Minimum</Text>
            </View>
            <View style={[styles.tempCard, styles.tempCardMid]}>
              <Text style={[styles.tempValue, { color: '#0D9488' }]}>{data.avg_temperature}°C</Text>
              <Text style={styles.tempLabel}>Average</Text>
            </View>
            <View style={styles.tempCard}>
              <Text style={styles.tempValue}>{data.max_temperature}°C</Text>
              <Text style={styles.tempLabel}>Maximum</Text>
            </View>
          </View>
        </Animatable.View>

        {/* Hourly Breakdown */}
        {data.hourly_posture && data.hourly_posture.length > 0 && (
          <Animatable.View animation="fadeInUp" delay={600} style={styles.section}>
            <Text style={styles.sectionTitle}>🕐 Hourly Posture</Text>
            {data.hourly_posture.map((h, index) => {
              const goodPct = h.total > 0 ? Math.round((h.good / h.total) * 100) : 0;
              return (
                <Animatable.View
                  key={h.hour}
                  animation="fadeInLeft"
                  delay={700 + index * 80}
                  style={styles.hourRow}
                >
                  <Text style={styles.hourLabel}>{h.label}</Text>
                  <View style={styles.barBg}>
                    <View
                      style={[
                        styles.barFill,
                        {
                          width: `${goodPct}%`,
                          backgroundColor: goodPct >= 70 ? '#10B981' : goodPct >= 40 ? '#F59E0B' : '#EF4444'
                        }
                      ]}
                    />
                  </View>
                  <Text style={styles.barPct}>{goodPct}%</Text>
                </Animatable.View>
              );
            })}
          </Animatable.View>
        )}

        {/* Recommendations */}
        <Animatable.View animation="fadeInUp" delay={700} style={styles.section}>
          <Text style={styles.sectionTitle}>💡 Recommendations</Text>
          {data.recommendations.map((rec, index) => (
            <Animatable.View
              key={index}
              animation="fadeInLeft"
              delay={800 + index * 150}
              style={[
                styles.recCard,
                rec.type === 'success' && styles.recSuccess,
                rec.type === 'warning' && styles.recWarning,
                rec.type === 'error' && styles.recError,
              ]}
            >
              <Text style={styles.recIcon}>{rec.icon}</Text>
              <View style={styles.recContent}>
                <Text style={styles.recTitle}>{rec.title}</Text>
                <Text style={styles.recText}>{rec.text}</Text>
              </View>
            </Animatable.View>
          ))}
        </Animatable.View>

        {/* Bottom spacing */}
        <View style={{ height: 40 }} />

      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },
  center: {
    flex: 1,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loadingText: {
    color: '#94A3B8',
    marginTop: 16,
    fontSize: 15,
  },
  errorEmoji: {
    fontSize: 50,
    marginBottom: 16,
  },
  errorText: {
    color: '#F87171',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  backBtn: {
    backgroundColor: '#0D9488',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  backBtnText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  // Hero
  hero: {
    padding: 28,
    paddingTop: 60,
    alignItems: 'center',
  },
  backArrow: {
    position: 'absolute',
    top: 60,
    left: 20,
  },
  backArrowText: {
    color: '#A7F3D0',
    fontSize: 15,
  },
  dateLabel: {
    color: '#A7F3D0',
    fontSize: 13,
    marginBottom: 4,
  },
  heroTitle: {
    color: '#fff',
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  scoreText: {
    fontSize: 80,
    fontWeight: 'bold',
  },
  scoreLabel: {
    color: '#94A3B8',
    fontSize: 14,
    marginTop: 4,
  },
  // Body
  body: {
    padding: 16,
  },
  // Stats
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
    backgroundColor: '#1E293B',
    borderRadius: 16,
    padding: 12,
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 3,
  },
  statEmoji: {
    fontSize: 22,
    marginBottom: 4,
  },
  statValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  statLabel: {
    color: '#64748B',
    fontSize: 10,
    marginTop: 2,
    textAlign: 'center',
  },
  // Section
  section: {
    backgroundColor: '#1E293B',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  // Bars
  barWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  barLabel: {
    color: '#CBD5E1',
    width: 55,
    fontSize: 13,
  },
  barBg: {
    flex: 1,
    backgroundColor: '#334155',
    borderRadius: 8,
    height: 12,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 8,
  },
  barPct: {
    color: '#94A3B8',
    width: 38,
    textAlign: 'right',
    fontSize: 12,
  },
  // Temperature
  tempRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  tempCard: {
    flex: 1,
    backgroundColor: '#0F172A',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  tempCardMid: {
    borderWidth: 1,
    borderColor: '#0D9488',
  },
  tempValue: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  tempLabel: {
    color: '#64748B',
    fontSize: 12,
    marginTop: 4,
  },
  // Hourly
  hourRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  hourLabel: {
    color: '#94A3B8',
    width: 45,
    fontSize: 12,
  },
  // Recommendations
  recCard: {
    flexDirection: 'row',
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderLeftWidth: 4,
    backgroundColor: '#0F172A',
  },
  recSuccess: { borderLeftColor: '#10B981' },
  recWarning: { borderLeftColor: '#F59E0B' },
  recError: { borderLeftColor: '#EF4444' },
  recIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  recContent: {
    flex: 1,
  },
  recTitle: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
    marginBottom: 4,
  },
  recText: {
    color: '#94A3B8',
    fontSize: 13,
    lineHeight: 19,
  },
});
