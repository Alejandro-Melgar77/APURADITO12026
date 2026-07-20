import '../../domain/entities/ride.dart';
import '../../domain/repositories/ride_repository.dart';

class RideRepositoryImpl implements RideRepository {
  @override
  Future<List<Ride>> getAvailableRides(
    String origin,
    String destination,
  ) async {
    // Mock implementation
    await Future.delayed(const Duration(seconds: 1));
    return [
      Ride(
        id: '1',
        driverId: 'driver1',
        origin: origin,
        destination: destination,
        price: 15.0,
        departureTime: DateTime.now().add(const Duration(hours: 1)),
      ),
    ];
  }

  @override
  Future<Ride> publishRide(Ride ride) async {
    // Mock implementation
    await Future.delayed(const Duration(seconds: 1));
    return ride;
  }
}
