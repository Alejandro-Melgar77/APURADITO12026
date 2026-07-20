import 'package:apuradito_mobile/core/network/api_client.dart';
import 'package:apuradito_mobile/core/network/connectivity_service.dart';
import 'package:apuradito_mobile/core/network/websocket_service.dart';
import 'package:apuradito_mobile/core/theme/app_theme.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/providers/driver_provider.dart';
import 'package:apuradito_mobile/presentation/providers/map_provider.dart';
import 'package:apuradito_mobile/presentation/providers/offline_sync_provider.dart';
import 'package:apuradito_mobile/presentation/providers/wallet_provider.dart';
import 'package:apuradito_mobile/presentation/screens/auth/login_screen.dart';
import 'package:apuradito_mobile/presentation/screens/auth/register_screen.dart';
import 'package:apuradito_mobile/presentation/screens/driver/active_ride_screen.dart';
import 'package:apuradito_mobile/presentation/screens/driver/driver_home_screen.dart';
import 'package:apuradito_mobile/presentation/screens/driver/manage_requests_screen.dart';
import 'package:apuradito_mobile/presentation/screens/driver/publish_route_screen.dart';
import 'package:apuradito_mobile/presentation/screens/passenger/passenger_home_screen.dart';
import 'package:apuradito_mobile/presentation/screens/passenger/passenger_trips_screen.dart';
import 'package:apuradito_mobile/presentation/screens/passenger/request_ride_screen.dart';
import 'package:apuradito_mobile/presentation/screens/passenger/ride_tracking_screen.dart';
import 'package:apuradito_mobile/presentation/screens/shared/profile_screen.dart';
import 'package:apuradito_mobile/presentation/screens/shared/wallet_screen.dart';
import 'package:apuradito_mobile/presentation/screens/splash_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  ApiClient().initialize();
  final ConnectivityService connectivityService = ConnectivityService();
  await connectivityService.initialize();
  final AuthProvider authProvider = AuthProvider();
  await authProvider.loadSavedUser();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider<AuthProvider>.value(value: authProvider),
        ChangeNotifierProvider<ConnectivityService>.value(
          value: connectivityService,
        ),
        ChangeNotifierProvider<OfflineSyncProvider>(
          create: (_) => OfflineSyncProvider(),
        ),
        ChangeNotifierProvider<MapProvider>(create: (_) => MapProvider()),
        ChangeNotifierProvider<WebSocketService>(
            create: (_) => WebSocketService()),
        ChangeNotifierProvider<DriverProvider>(create: (_) => DriverProvider()),
        ChangeNotifierProvider<WalletProvider>(create: (_) => WalletProvider()),
      ],
      child: ApuraditoApp(authProvider: authProvider),
    ),
  );
}

class ApuraditoApp extends StatefulWidget {
  const ApuraditoApp({super.key, required this.authProvider});

  final AuthProvider authProvider;

  @override
  State<ApuraditoApp> createState() => _ApuraditoAppState();
}

class _ApuraditoAppState extends State<ApuraditoApp> {
  @override
  void initState() {
    super.initState();
    widget.authProvider.addListener(_configureOfflineSync);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _configureOfflineSync();
  }

  void _configureOfflineSync() {
    if (!mounted) return;
    context.read<OfflineSyncProvider>().configure(
          context.read<ConnectivityService>(),
          widget.authProvider.currentUser?.id,
        );
  }

  @override
  void dispose() {
    widget.authProvider.removeListener(_configureOfflineSync);
    super.dispose();
  }

  late final GoRouter _router = GoRouter(
    initialLocation: '/',
    refreshListenable: widget.authProvider,
    redirect: (BuildContext context, GoRouterState state) {
      final bool isSplash = state.matchedLocation == '/';
      final bool isAuthRoute = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';
      final bool loggedIn = widget.authProvider.isLoggedIn;
      final bool isDriver = widget.authProvider.activeRol == 'conductor';

      if (isSplash) return null;
      if (!loggedIn && !isAuthRoute) return '/login';
      if (loggedIn && isAuthRoute) return isDriver ? '/driver' : '/passenger';
      if (loggedIn && state.matchedLocation.startsWith('/driver') && !isDriver)
        return '/passenger';
      return null;
    },
    routes: <RouteBase>[
      GoRoute(path: '/', builder: (_, __) => const SplashScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(
          path: '/passenger', builder: (_, __) => const PassengerHomeScreen()),
      GoRoute(
        path: '/passenger/trips',
        builder: (_, __) => const PassengerTripsScreen(),
      ),
      GoRoute(
        path: '/passenger/request/:routeId',
        builder: (_, GoRouterState state) => RequestRideScreen(
          routeId: state.pathParameters['routeId']!,
        ),
      ),
      GoRoute(
        path: '/passenger/tracking/:routeId',
        builder: (_, GoRouterState state) => RideTrackingScreen(
          routeId: state.pathParameters['routeId']!,
        ),
      ),
      GoRoute(path: '/driver', builder: (_, __) => const DriverHomeScreen()),
      GoRoute(
          path: '/driver/publish',
          builder: (_, __) => const PublishRouteScreen()),
      GoRoute(
          path: '/driver/requests',
          builder: (_, __) => const ManageRequestsScreen()),
      GoRoute(
          path: '/driver/active', builder: (_, __) => const ActiveRideScreen()),
      GoRoute(path: '/shared/wallet', builder: (_, __) => const WalletScreen()),
      GoRoute(
          path: '/shared/profile', builder: (_, __) => const ProfileScreen()),
    ],
  );

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Apuradito',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: _router,
      builder: (BuildContext context, Widget? child) => _ConnectivityShell(
        child: child ?? const SizedBox.shrink(),
      ),
    );
  }
}

class _ConnectivityShell extends StatefulWidget {
  const _ConnectivityShell({required this.child});

  final Widget child;

  @override
  State<_ConnectivityShell> createState() => _ConnectivityShellState();
}

class _ConnectivityShellState extends State<_ConnectivityShell>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      context.read<ConnectivityService>().refresh();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool online = context.watch<ConnectivityService>().isOnline;
    final OfflineSyncProvider sync = context.watch<OfflineSyncProvider>();
    return Stack(
      children: <Widget>[
        widget.child,
        if (!online)
          const Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              bottom: false,
              child: _OfflineBanner(),
            ),
          )
        else if (sync.pendingCount > 0)
          Positioned(
            right: 12,
            bottom: 12,
            child: SafeArea(
              child: ActionChip(
                avatar: sync.isSyncing
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.sync, size: 18),
                label: Text('${sync.pendingCount} pendiente(s)'),
                onPressed: sync.isSyncing ? null : sync.sync,
              ),
            ),
          ),
      ],
    );
  }
}

class _OfflineBanner extends StatelessWidget {
  const _OfflineBanner();

  @override
  Widget build(BuildContext context) => Material(
        color: const Color(0xFFB45309),
        child: const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: <Widget>[
              Icon(Icons.cloud_off, color: Colors.white, size: 18),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Sin conexion: estas viendo informacion guardada.',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
        ),
      );
}
