import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, KeyboardAvoidingView, Platform,
  Alert, ActivityIndicator, ScrollView
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Animatable from 'react-native-animatable';
import { login, signup } from '../api/apiService';

export default function LoginScreen({ navigation }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!isLogin && name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Enter a valid email address';
    }
    if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      if (isLogin) {
        const response = await login(email, password);
        await AsyncStorage.setItem('token', response.data.token);
        await AsyncStorage.setItem('userName', response.data.name);
        navigation.replace('Calendar');
      } else {
        await signup(name, email, password);
        Alert.alert('Success!', 'Account created. Please log in.');
        setIsLogin(true);
      }
    } catch (err) {
      Alert.alert('Error', err.response?.data?.error || 'Something went wrong. Check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={['#0D9488', '#0F172A']} style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inner}
      >
        <ScrollView showsVerticalScrollIndicator={false}>

          {/* Header */}
          <Animatable.View animation="fadeInDown" duration={800} style={styles.header}>
            <Text style={styles.emoji}>🪑</Text>
            <Text style={styles.title}>Smart Chair</Text>
            <Text style={styles.subtitle}>Posture & Health Monitor</Text>
          </Animatable.View>

          {/* Card */}
          <Animatable.View animation="fadeInUp" duration={800} delay={200} style={styles.card}>
            <Text style={styles.cardTitle}>
              {isLogin ? 'Welcome Back 👋' : 'Create Account'}
            </Text>

            {/* Name Field — only for signup */}
            {!isLogin && (
              <View style={styles.inputWrap}>
                <Text style={styles.label}>Full Name</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Enter your name"
                  placeholderTextColor="#475569"
                  value={name}
                  onChangeText={setName}
                />
                {errors.name && <Text style={styles.error}>{errors.name}</Text>}
              </View>
            )}

            {/* Email Field */}
            <View style={styles.inputWrap}>
              <Text style={styles.label}>Email</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter your email"
                placeholderTextColor="#475569"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
              {errors.email && <Text style={styles.error}>{errors.email}</Text>}
            </View>

            {/* Password Field */}
            <View style={styles.inputWrap}>
              <Text style={styles.label}>Password</Text>
              <TextInput
                style={styles.input}
                placeholder="Minimum 6 characters"
                placeholderTextColor="#475569"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
              {errors.password && <Text style={styles.error}>{errors.password}</Text>}
            </View>

            {/* Submit Button */}
            <TouchableOpacity
              style={styles.btn}
              onPress={handleSubmit}
              disabled={loading}
            >
              {loading
                ? <ActivityIndicator color="#fff" />
                : <Text style={styles.btnText}>
                    {isLogin ? 'Log In' : 'Sign Up'}
                  </Text>
              }
            </TouchableOpacity>

            {/* Toggle Login/Signup */}
            <TouchableOpacity
              onPress={() => {
                setIsLogin(!isLogin);
                setErrors({});
              }}
              style={styles.toggle}
            >
              <Text style={styles.toggleText}>
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <Text style={styles.toggleLink}>
                  {isLogin ? 'Sign Up' : 'Log In'}
                </Text>
              </Text>
            </TouchableOpacity>

          </Animatable.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  inner: {
    flex: 1,
    padding: 24,
    paddingTop: 60,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  emoji: {
    fontSize: 70,
    marginBottom: 10,
  },
  title: {
    fontSize: 34,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    color: '#A7F3D0',
    fontSize: 15,
    marginTop: 6,
  },
  card: {
    backgroundColor: '#1E293B',
    borderRadius: 24,
    padding: 28,
    shadowColor: '#000',
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 8,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 24,
  },
  inputWrap: {
    marginBottom: 16,
  },
  label: {
    color: '#94A3B8',
    fontSize: 13,
    marginBottom: 6,
    marginLeft: 2,
  },
  input: {
    backgroundColor: '#0F172A',
    color: '#fff',
    padding: 14,
    borderRadius: 12,
    fontSize: 15,
    borderWidth: 1,
    borderColor: '#334155',
  },
  error: {
    color: '#F87171',
    fontSize: 12,
    marginTop: 5,
    marginLeft: 2,
  },
  btn: {
    backgroundColor: '#0D9488',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  btnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  toggle: {
    marginTop: 20,
    alignItems: 'center',
  },
  toggleText: {
    color: '#94A3B8',
    fontSize: 14,
  },
  toggleLink: {
    color: '#0D9488',
    fontWeight: 'bold',
  },
});
