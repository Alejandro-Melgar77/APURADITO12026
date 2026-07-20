import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/core/network/websocket_service.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';
import 'package:apuradito_mobile/presentation/screens/splash_screen.dart';
import 'package:apuradito_mobile/presentation/screens/auth/login_screen.dart';
import 'package:apuradito_mobile/presentation/screens/auth/register_screen.dart';
import 'package:apuradito_mobile/presentation/screens/passenger/passenger_home_screen.dart';
import 'package:apuradito_mobile/presentation/screens/passenger/ride_tracking_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  ApiClient().initialize();
  
  final authProvider = AuthProvider();
  await authProvider.loadSavedUser();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider),
        ChangeNotifierProvider(create: (_) => MapProvider()),
        ChangeNotifierProvider(create: (_) => WebSocketService()),
      ],
      child: const ApuraditoApp(),
    ),
  );
}

class ApuraditoApp extends StatelessWidget {
  const ApuraditoApp({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    final router = GoRouter(
      initialLocation: '/',
      redirect: (context, state) {
        final isLoggedIn = authProvider.isLoggedIn;
        final isAuthRoute = state.matchedLocation == '/login' || state.matchedLocation == '/register';
        final isSplash = state.matchedLocation == '/';

        if (!isLoggedIn && !isAuthRoute && !isSplash) {
          return '/login';
        }
        return null;
      },
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const SplashScreen(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/register',
          builder: (context, state) => const RegisterScreen(),
        ),
        GoRoute(
          path: '/passenger',
          builder: (context, state) => const PassengerHomeScreen(),
        ),
        GoRoute(
          path: '/passenger/tracking/:routeId',
          builder: (context, state) => RideTrackingScreen(
            routeId: state.pathParameters['routeId']!,
          ),
        ),
        // Placeholders for other screens as per prompt:
        GoRoute(
          path: '/driver',
          builder: (context, state) => const Scaffold(body: Center(child: Text('Driver Home'))),
        ),
        GoRoute(
          path: '/driver/publish',
          builder: (context, state) => const Scaffold(body: Center(child: Text('Publish Route'))),
        ),
        GoRoute(
          path: '/driver/requests',
          builder: (context, state) => const Scaffold(body: Center(child: Text('Manage Requests'))),
        ),
        GoRoute(
          path: '/shared/wallet',
          builder: (context, state) => const Scaffold(body: Center(child: Text('Wallet'))),
        ),
        GoRoute(
          path: '/shared/profile',
          builder: (context, state) => const Scaffold(body: Center(child: Text('Profile'))),
        ),
      ],
    );

    return MaterialApp.router(
      title: 'Apuradito',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: router,
    );
  }
}
