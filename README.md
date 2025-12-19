# System Sterowania Robotem Szachowym

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20%7C%20Arduino-orange.svg)

**Temat:** System szachowy z wykorzystaniem wizji komputerowej i automatycznej manipulacji.  
**Autor:** Piotr Pyzik  
**Uczelnia:** Politechnika Wrocławska, Wydział Elektroniki, Fotoniki i Mikrosystemów (2025).

---

## Opis Projektu

Repozytorium zawiera kod źródłowy oprogramowania sterującego dla autonomicznego robota szachowego. System integruje trzy kluczowe dziedziny:
1.  **Wizję komputerową** – do detekcji ruchów gracza na fizycznej planszy.
2.  **Sztuczną inteligencję** – silnik Stockfish do analizy gry i podejmowania decyzji.
3.  **Sterowanie maszynowe** – obsługa manipulatora kartezjańskiego (CNC) z chwytakiem elektromagnetycznym.

## Struktura Repozytorium

Kod został podzielony na moduły odpowiedzialne za poszczególne warstwy systemu:

### 1. `test5.py` (Główny Kontroler)
Plik wykonywalny realizujący główną pętlę gry (*Main Loop*).
* **Funkcjonalność:**
    * Inicjalizacja połączenia z Arduino i silnikiem Stockfish.
    * Sekwencyjna obsługa gry: *Ruch Gracza -> Detekcja -> Walidacja -> Ruch Komputera*.
    * Obsługa zdarzeń specjalnych: promocja piona, roszada, bicie.
    * Interfejs użytkownika (HMI) oparty na zdarzeniach klawiatury.

### 2. `utils3.py` (Moduł Wizyjny)
Warstwa odpowiedzialna za przetwarzanie obrazu i cyfrową reprezentację szachownicy.
* **Klasa `Field`:** Obiektowa reprezentacja pola szachowego. Przechowuje historię obrazów i obliczony współczynnik zmian.
* **Algorytm Hybrydowy:** Implementacja autorskiego podejścia do detekcji ruchu, łączącego:
    * **SSIM (Structural Similarity Index):** Odporność na zmiany oświetlenia i cienie.
    * **Analizę barwną (CIE Lab):** Precyzyjna detekcja zmian kolorystycznych.
* **Kalibracja:** Funkcja `setupBorders()` umożliwiająca manualne dopasowanie obszaru roboczego (ROI) do obrazu z kamery.
* **Diagnostyka:** Funkcja `plot_debug_graphs()` generująca mapy ciepła (Heatmaps) dla celów debugowania algorytmu.

### 3. `cnc.py` (Warstwa Sprzętowa)
Interfejs komunikacyjny dla sterownika GRBL i obsługa kinematyki robota.
* **Komunikacja:** Szeregowa transmisja komend G-code (protokół "Send-and-Wait").
* **Dynamiczna oś Z:** Funkcja `movePiece` dostosowuje wysokość opuszczania chwytaka do typu figury (zdefiniowane w słowniku `piece_height`), zapobiegając kolizjom.
* **Konfiguracja:** Funkcja `GRBLSetup` automatycznie konfiguruje parametry sterownika (kroki/mm, przyspieszenia) przy każdym uruchomieniu.
