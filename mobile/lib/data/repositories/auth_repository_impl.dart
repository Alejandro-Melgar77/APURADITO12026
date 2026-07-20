import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  @override
  Future<User> login(String email, String password) async {
    // Mock implementation
    await Future.delayed(const Duration(seconds: 1));
    return User(id: '1', name: 'Test User', email: email, isDriver: false);
  }

  @override
  Future<User> register(
    String name,
    String email,
    String password,
    bool isDriver,
  ) async {
    // Mock implementation
    await Future.delayed(const Duration(seconds: 1));
    return User(id: '1', name: name, email: email, isDriver: isDriver);
  }

  @override
  Future<void> logout() async {
    await Future.delayed(const Duration(seconds: 1));
  }
}
