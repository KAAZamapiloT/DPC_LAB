/*
    CS-302 | Distributed & Parallel Computing Lab Assignment
    Operation Staff-WiFi

    Student 1 ID: 202351150  -> last 4 digits = 1150
    Student 2 ID: 202351130  -> last 4 digits = 1130

    Build:
        mpic++ -O2 -std=c++17 affine.cpp -o solution

    Run:

        mpirun -np 2 ./solution
*/

#include <mpi.h>
#include <iostream>
#include <cstdint>

using std::cout;
using std::cerr;

using i64  = long long;
using i128 = __int128_t;

static constexpr i64 NumIter = 2000000000LL;

static i64 NormMod(i64 X, i64 Mod) {
    X %= Mod;
    if (X < 0) X += Mod;
    return X;
}

static i64 MulMod(i64 X, i64 Y, i64 Mod) {
    return (i64)((i128)X * Y % Mod);
}

static i64 PowMod(i64 X, i64 Exp, i64 Mod) {
    if (Mod == 1) return 0;
    i64 Result = 1;
    X = NormMod(X, Mod);
    while (Exp > 0) {
        if (Exp & 1LL) Result = MulMod(Result, X, Mod);
        X   = MulMod(X, X, Mod);
        Exp >>= 1LL;
    }
    return Result;
}

static i64 ModInv(i64 X, i64 P) {
    return PowMod(X, P - 2, P);
}


class Grinder {
public:
    static i64 Run(i64 Seed, i64 M, i64 A, i64 Mod) {
        if (Mod == 1) return 0;

        i64 S  = NormMod(Seed, Mod);
        i64 Mv = NormMod(M,    Mod);
        i64 Av = NormMod(A,    Mod);

        i64 MN = PowMod(Mv, NumIter, Mod);

        if (Mv == 1) {
            i64 NmodP = (i64)((i128)NumIter % Mod);
            return (S + MulMod(NmodP, Av, Mod)) % Mod;
        }

        i64 Term1 = MulMod(MN, S, Mod);
        i64 MNm1  = (MN - 1 + Mod) % Mod;
        i64 Inv   = ModInv((Mv - 1 + Mod) % Mod, Mod);
        i64 Term2 = MulMod(MulMod(Av, MNm1, Mod), Inv, Mod);
        return (Term1 + Term2) % Mod;
    }
};

class Worker {
public:
    Worker(i64 KeyA, i64 KeyB) : KeyA(KeyA), KeyB(KeyB) {}
    virtual ~Worker() = default;

    virtual void Execute() = 0;

protected:
    const i64 KeyA, KeyB;
    i64 Alpha = 0, Beta = 0, Verify = 0, VerifyOther = 0;
};


class StudentOne : public Worker {
public:
    StudentOne(i64 KeyA, i64 KeyB) : Worker(KeyA, KeyB) {}

    void Execute() override {
        // Steps 1a-1c: compute α
        i64 AlphaPrime       = Grinder::Run(KeyA,       31, 17, 9973);
        i64 AlphaDoublePrime = Grinder::Run(AlphaPrime, 37, 11, 9973);
        Alpha                = (AlphaPrime + AlphaDoublePrime) % 9973;

        // Send α; wait for β (rank 1 needs α first to compute β)
        MPI_Send(&Alpha, 1, MPI_LONG_LONG, 1, 0, MPI_COMM_WORLD);
        MPI_Recv(&Beta,  1, MPI_LONG_LONG, 1, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        // Step 3: both compute Verify independently; exchange to confirm match
        Verify = Grinder::Run(Alpha + Beta, 7, 3, 101);

        MPI_Sendrecv(
            &Verify,      1, MPI_LONG_LONG, 1, 2,
            &VerifyOther, 1, MPI_LONG_LONG, 1, 2,
            MPI_COMM_WORLD, MPI_STATUS_IGNORE
        );

        // Steps 4-5: compute R and final 4-digit Password
        i64 R        = Grinder::Run(Alpha * Beta + KeyA + KeyB, 13, 7, 9973);
        i64 Password = R % 10000;

        // ── Output ───────────────────────────────────────────────────────────
        cout << "A = "            << KeyA        << "\n";
        cout << "B = "            << KeyB        << "\n";
        cout << "alpha = "        << Alpha       << "\n";
        cout << "beta  = "        << Beta        << "\n";
        cout << "verify = "       << Verify      << "\n";
        cout << "verify_other = " << VerifyOther << "\n";

        if (Verify == VerifyOther)
            cout << "Verify matched.\n";
        else
            cout << "Verify mismatch!\n";

        cout << "R = "        << R        << "\n";
        cout << "Password = " << Password << "\n";
    }
};


class StudentTwo : public Worker {
public:
    StudentTwo(i64 KeyA, i64 KeyB) : Worker(KeyA, KeyB) {}

    void Execute() override {
        // Receive α from Student 1
        MPI_Recv(&Alpha, 1, MPI_LONG_LONG, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        // Steps 2a-2c: compute β using received α
        i64 BetaPrime       = Grinder::Run(Alpha,     KeyB, 13, 9973);
        i64 BetaDoublePrime = Grinder::Run(BetaPrime,   41, 19, 9973);
        Beta                = (BetaPrime + BetaDoublePrime) % 9973;

        // Send β back
        MPI_Send(&Beta, 1, MPI_LONG_LONG, 0, 1, MPI_COMM_WORLD);

        // Step 3: both compute Verify independently; exchange to confirm match
        Verify = Grinder::Run(Alpha + Beta, 7, 3, 101);

        MPI_Sendrecv(
            &Verify,      1, MPI_LONG_LONG, 0, 2,
            &VerifyOther, 1, MPI_LONG_LONG, 0, 2,
            MPI_COMM_WORLD, MPI_STATUS_IGNORE
        );
    }
};

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int Rank = 0, Size = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &Rank);
    MPI_Comm_size(MPI_COMM_WORLD, &Size);

    if (Size != 2) {
        if (Rank == 0)
            cerr << "Run this program with exactly 2 MPI processes.\n";
        MPI_Finalize();
        return 0;
    }

    const i64 KeyA = 1088; // Student 1: last 4 digits of ID
    const i64 KeyB = 1086; // Student 2: last 4 digits of ID

    MPI_Barrier(MPI_COMM_WORLD);
    double StartTime = MPI_Wtime();

    if (Rank == 0) {
        StudentOne S1(KeyA, KeyB);
        S1.Execute();
    } else {
        StudentTwo S2(KeyA, KeyB);
        S2.Execute();
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double LocalTime = MPI_Wtime() - StartTime;
    double TotalTime = 0.0;

    MPI_Reduce(&LocalTime, &TotalTime, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if (Rank == 0)
        cout << "Total computation time (seconds) = " << TotalTime << "\n";

    MPI_Finalize();
    return 0;
}
