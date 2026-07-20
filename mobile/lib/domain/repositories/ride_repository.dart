import '../entities/ride.dart';

abstract class RideRepository {
  Future<List<Ride>> getAvailableRides(String origin, String destination);
  Future<Ride> publishRide(Ride ride);
}
