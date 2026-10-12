import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import * as Animatable from 'react-native-animatable';

export default function PostureAnimation({ score }) {
  const isGood = score >= 70;
  const isBad = score < 40;
  const isFair = score >= 40 && score < 70;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Posture Visualization</Text>

      <View style={styles.figureContainer}>

        {/* Chair */}
        <View style={styles.chairBack} />
        <View style={styles.chairSeat} />

        {/* Person */}
        {/* Head */}
        <Animatable.View
          animation={isGood ? 'pulse' : 'shake'}
          iterationCount="infinite"
          duration={isGood ? 2000 : 3000}
          style={styles.head}
        />

        {/* Body */}
        <Animatable.View
          animation={isBad ? 'wobble' : undefined}
          iterationCount={isBad ? 'infinite' : 1}
          duration={2000}
          style={[
            styles.body,
            isBad && styles.bodyBad,
            isFair && styles.bodyFair,
          ]}
        />

        {/* Arms */}
        <View style={styles.armsContainer}>
          <View style={[styles.arm, isBad && styles.armBad]} />
          <View style={[styles.arm, isBad && styles.armBad]} />
        </View>

        {/* Legs */}
        <View style={styles.legsContainer}>
          <View style={styles.leg} />
          <View style={styles.leg} />
        </View>

      </View>

      {/* Status Label */}
      <Animatable.Text
        animation="bounceIn"
        delay={400}
        style={[
          styles.statusLabel,
          isGood && styles.good,
          isBad && styles.bad,
          isFair && styles.fair,
        ]}
      >
        {isGood ? '✅ Good Posture' : isBad ? '❌ Poor Posture — Sit Straight!' : '⚠️ Fair Posture'}
      </Animatable.Text>

      {/* Tip */}
      <Text style={styles.tip}>
        {isGood
          ? 'Your spine alignment is great today!'
          : isBad
          ? 'Try sitting with your back fully against the chair.'
          : 'A few adjustments will improve your posture.'}
      </Text>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1E293B',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
  },
  title: {
    color: '#94A3B8',
    fontSize: 14,
    marginBottom: 20,
    fontWeight: '600',
  },
  figureContainer: {
    height: 180,
    width: 120,
    alignItems: 'center',
    position: 'relative',
    marginBottom: 16,
  },
  // Chair
  chairBack: {
    position: 'absolute',
    right: 10,
    top: 30,
    width: 8,
    height: 100,
    backgroundColor: '#334155',
    borderRadius: 4,
  },
  chairSeat: {
    position: 'absolute',
    bottom: 40,
    width: 80,
    height: 10,
    backgroundColor: '#334155',
    borderRadius: 4,
  },
  // Person
  head: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#0D9488',
    marginBottom: 4,
    marginTop: 10,
  },
  body: {
    width: 22,
    height: 55,
    backgroundColor: '#0D9488',
    borderRadius: 8,
    marginTop: 2,
  },
  bodyBad: {
    transform: [{ rotate: '20deg' }],
    backgroundColor: '#EF4444',
  },
  bodyFair: {
    transform: [{ rotate: '8deg' }],
    backgroundColor: '#F59E0B',
  },
  armsContainer: {
    flexDirection: 'row',
    gap: 30,
    position: 'absolute',
    top: 80,
  },
  arm: {
    width: 10,
    height: 35,
    backgroundColor: '#134E4A',
    borderRadius: 5,
  },
  armBad: {
    transform: [{ rotate: '25deg' }],
    backgroundColor: '#7F1D1D',
  },
  legsContainer: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 4,
  },
  leg: {
    width: 12,
    height: 45,
    backgroundColor: '#134E4A',
    borderRadius: 5,
  },
  // Labels
  statusLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  good: { color: '#10B981' },
  bad: { color: '#EF4444' },
  fair: { color: '#F59E0B' },
  tip: {
    color: '#64748B',
    fontSize: 13,
    textAlign: 'center',
  },
});