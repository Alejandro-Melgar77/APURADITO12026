import 'package:apuradito_mobile/main.dart';
import 'package:apuradito_mobile/core/network/connectivity_service.dart';
import 'package:apuradito_mobile/presentation/providers/auth_provider.dart';
import 'package:apuradito_mobile/presentation/providers/offline_sync_provider.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

void main() {
  testWidgets('muestra la pantalla de inicio sin el contador de plantilla',
      (WidgetTester tester) async {
    final AuthProvider authProvider = AuthProvider();
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider<AuthProvider>.value(value: authProvider),
          ChangeNotifierProvider<ConnectivityService>(
            create: (_) => ConnectivityService(),
          ),
          ChangeNotifierProvider<OfflineSyncProvider>(
            create: (_) => OfflineSyncProvider(),
          ),
        ],
        child: ApuraditoApp(authProvider: authProvider),
      ),
    );

    expect(find.text('Apuradito'), findsOneWidget);
    expect(find.text('0'), findsNothing);
  });
}
