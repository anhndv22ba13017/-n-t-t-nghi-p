# Hướng Dẫn Viết Báo Cáo Đồ Án Bằng LaTeX

Viết báo cáo Đồ án bằng **LaTeX** là một lựa chọn cực kỳ chuyên nghiệp. Nó giúp văn bản tự động căn lề chuẩn xác, tự động làm mục lục, đánh số hình ảnh/bảng biểu và công thức toán học vô cùng đẹp mắt mà Word khó sánh bằng.

> [!TIP]
> **Cách dễ nhất để bắt đầu:** Đừng cài đặt LaTeX lên máy tính cho nặng máy. Hãy sử dụng trang web **[Overleaf.com](https://www.overleaf.com/)**. Đây là "Google Docs" dành riêng cho LaTeX. Bạn chỉ cần tạo tài khoản, tạo Project mới (Blank Project) và dán đoạn code bên dưới vào là xong!

## Cấu Trúc Khung (Template) LaTeX Dành Riêng Cho Đồ Án Của Bạn

Dưới đây là một bộ khung chuẩn chỉnh, đã hỗ trợ 100% tiếng Việt có dấu. Bạn hãy copy toàn bộ đoạn code này dán đè lên file `main.tex` trên Overleaf:

```latex
\documentclass[a4paper,12pt]{report}

% --- CÁC GÓI THƯ VIỆN CẦN THIẾT ---
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc} % Hỗ trợ tiếng Việt trọn vẹn
\usepackage[vietnamese]{babel} % Dịch các chữ tự động như Chapter -> Chương
\usepackage{graphicx} % Hỗ trợ chèn ảnh
\usepackage{hyperref} % Tạo link click được trong mục lục
\usepackage{booktabs} % Hỗ trợ vẽ bảng biểu đẹp mắt
\usepackage{geometry} % Căn lề chuẩn đồ án
\geometry{
    a4paper,
    left=30mm,
    right=20mm,
    top=20mm,
    bottom=20mm,
}

% --- THÔNG TIN TRANG BÌA ---
\title{BÁO CÁO ĐỒ ÁN TỐT NGHIỆP \\ \Large HỆ THỐNG TỰ ĐỘNG HÓA SẢN XUẤT VIDEO \\ BẰNG TRÍ TUỆ NHÂN TẠO (AI VIDEO ASSISTANT)}
\author{Sinh viên thực hiện: [Tên của bạn]}
\date{\today}

\begin{document}

% Tạo trang bìa và mục lục tự động
\maketitle
\tableofcontents
\newpage

% ---------------------------------------------------
\chapter{Mở Đầu}
% ---------------------------------------------------

\section{Lý do chọn đề tài}
Trong thời đại bùng nổ nội dung số, việc sản xuất video đòi hỏi quá nhiều công đoạn thủ công như lên kịch bản, tìm ảnh minh họa, thu âm và dựng phim. Đồ án này đề xuất một giải pháp tự động hóa toàn bộ quy trình trên dựa vào trí tuệ nhân tạo (AI).

\section{Mục tiêu đề tài}
Xây dựng thành công một pipeline (đường ống) khép kín từ văn bản đầu vào cho đến khi xuất ra file Timeline \textbf{.fcpxml} tự động chèn vào phần mềm DaVinci Resolve.

% ---------------------------------------------------
\chapter{Cơ Sở Lý Thuyết}
% ---------------------------------------------------

\section{Mô hình Ngôn ngữ Lớn (LLMs) trong phân tích ngữ cảnh}
Phân tích cách Qwen2.5-7B-Instruct trích xuất từ khóa và tông giọng.

\section{Hệ thống Sinh Giọng Nói (TTS) và Qwen3-TTS}
Giới thiệu về kiến trúc Transformer trong việc tổng hợp giọng nói.

\section{Tìm kiếm Hình ảnh bằng Vector (FAISS và CLIP)}
Trình bày nguyên lý chuyển đổi hình ảnh và văn bản thành chuỗi số (vector embeddings) để so sánh độ tương đồng ngữ nghĩa thay vì so sánh từ khóa thô.

% ---------------------------------------------------
\chapter{Kiến Trúc Và Cài Đặt Hệ Thống}
% ---------------------------------------------------

\section{Tổng quan đường ống (Pipeline) AI Video Assistant}
Hệ thống bao gồm các module chính: \textit{Phân tích Kịch bản, Truy xuất Hình ảnh, Sinh Giọng nói, và Lắp ráp Timeline}.

\section{Xử lý rào cản phần cứng với Kaggle}
Trình bày về các kỹ thuật Quantization (8-bit) và xử lý lỗi tràn RAM (OOM) khi huấn luyện mô hình Qwen3-TTS trên nền tảng Kaggle với giới hạn 19.5GB ổ cứng.

% ---------------------------------------------------
\chapter{Thực Nghiệm Và Đánh Giá}
% ---------------------------------------------------

\section{Đánh giá định lượng mô hình Sinh Giọng Nói}
Để chứng minh tính hiệu quả của mô hình một cách khách quan, đồ án đã triển khai hệ thống đánh giá tự động sử dụng mô hình nhận diện giọng nói Faster-Whisper.

\subsection{Kết quả Tỷ lệ lỗi từ (Word Error Rate - WER)}
Kết quả đánh giá cho thấy mô hình đạt điểm số WER trung bình là \textbf{15.75\%}.

% Ví dụ cách tạo Bảng trong LaTeX
\begin{table}[h!]
    \centering
    \begin{tabular}{@{}lcc@{}}
        \toprule
        \textbf{Phương pháp đánh giá} & \textbf{Tập dữ liệu} & \textbf{Chỉ số WER} \\ \midrule
        Faster-Whisper (small) & Test Manifest (8 mẫu) & 15.75\% \\ \bottomrule
    \end{tabular}
    \caption{Kết quả đánh giá định lượng mô hình TTS cá nhân hóa}
    \label{tab:wer_results}
\end{table}

\subsection{Phân tích lỗi thực tế}
Trong lĩnh vực TTS, mức độ lỗi dưới 20\% được coi là ngưỡng tiêu chuẩn rất cao để triển khai thực tế. Các lỗi nhỏ ghi nhận chủ yếu xuất phát từ hiện tượng Code-switching (đọc tiếng Anh xen lẫn tiếng Việt như từ "handshaking lemma") hoặc đọc các con số (1.000 likes) do thiếu bộ tiền xử lý chuẩn hóa văn bản. Tuy sai từ, âm điệu tổng thể vẫn giữ được độ tự nhiên và biểu cảm xuất sắc.

% ---------------------------------------------------
\chapter{Kết Luận}
% ---------------------------------------------------
Đồ án đã hoàn thành toàn bộ các mục tiêu cốt lõi đề ra, xây dựng thành công trợ lý AI tự động hóa dựng phim. Hướng phát triển tương lai sẽ tập trung tích hợp thêm bộ tiền xử lý chuẩn hóa văn bản (Text Normalization) để triệt tiêu các lỗi phát âm số liệu.

\end{document}
```

## Các Cú Pháp LaTeX Cơ Bản Bạn Cần Biết

- `\chapter{Tên chương}`, `\section{Tên mục}`, `\subsection{Mục nhỏ hơn}`: Dùng để phân cấp tiêu đề. Phần mềm sẽ **tự động** đưa các mục này vào mục lục ở đầu trang mà không lo bị xô lệch như Word.
- `\textbf{Chữ đậm}`, `\textit{Chữ in nghiêng}`: Dùng để định dạng chữ.
- Cặp lệnh `\begin{table}` và `\end{table}`: Dùng để chèn bảng biểu (Như ví dụ ở Chương 4).

## Cách Chèn Ảnh Vào Báo Cáo
Để chèn một tấm ảnh (ví dụ sơ đồ kiến trúc hệ thống) vào LaTeX, bạn tải file ảnh đó lên Overleaf (nút Upload bên góc trái), đặt tên là `sodo.png` và dùng đoạn code sau:

```latex
\begin{figure}[h!]
    \centering
    \includegraphics[width=0.8\textwidth]{sodo.png}
    \caption{Sơ đồ tổng quan kiến trúc hệ thống AI Video Assistant}
    \label{fig:sodo_tongquan}
\end{figure}
```
Lợi ích cực lớn của LaTeX là hình ảnh sẽ tự động được căn giữa, tự động đánh số thứ tự "Hình 1.1: Sơ đồ..." ở bên dưới một cách chuẩn mực!
