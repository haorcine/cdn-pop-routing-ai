const REPORT_DATA = {

  meta: {
    generated_at: "Buoc 10 - tong hop cuoi cung",
    data_points_raw: 5180,
    data_points_pivot: 1294,
    days_by_region: [
      {region:"Bac", isp:"FPT", luot_do:400, so_ngay:7},
      {region:"Nam", isp:"VNPT", luot_do:532, so_ngay:11, ghi_chu:"co khoang nghi, thuc chat ~6.4 ngay lien tuc"},
      {region:"Trung", isp:"Viettel", luot_do:363, so_ngay:6, ghi_chu:"duoi moc toi thieu 7 ngay cua de cuong"}
    ],
    regions: ["Bac","Trung","Nam"],
    isps: ["VNPT","Viettel","FPT"],
    pops: ["cloudflare","vultr_singapore","vultr_seoul","linode_singapore"]
  },

  // ============================================================
  // 4.1 QUY TRINH LAM SACH DU LIEU  --  nguon: scripts/clean_data.py (chay that)
  // ============================================================
  cleaning: {
    tom_tat: {
      dong_doc_ban_dau: 5180,
      loai_thieu_latency_throughput: 1,
      loai_latency_throughput_khong_duong: 0,
      loai_trung_khoa_timestamp_vung_isp_pop: 0,
      dong_con_lai_data_sach: 5179
    },
    xu_ly_bat_thuong: {
      phuong_phap: "Danh dau cot bat_thuong=true, GIU LAI hoan toan khong xoa - vi day la tin hieu su co that, can thiet de lam nhan huan luyen cho Tang 2",
      tong_so_dong_danh_dau: 40,
      theo_vung_isp_pop: [
        {vung:"Bac", isp:"FPT", pop:"cloudflare", so_dong:15},
        {vung:"Bac", isp:"FPT", pop:"linode_singapore", so_dong:7},
        {vung:"Bac", isp:"FPT", pop:"vultr_seoul", so_dong:7},
        {vung:"Bac", isp:"FPT", pop:"vultr_singapore", so_dong:5},
        {vung:"Nam", isp:"VNPT", pop:"cloudflare", so_dong:1},
        {vung:"Nam", isp:"VNPT", pop:"linode_singapore", so_dong:3},
        {vung:"Nam", isp:"VNPT", pop:"vultr_singapore", so_dong:2}
      ]
    }
  },

  // ============================================================
  // 4.7 (phan lien quan train/test)  --  nguon: model/train_tier1.py (chay that)
  // ============================================================
  feature_engineering: {
    bien_nhan: "pop_toi_uu",
    so_lop: 4,
    danh_sach_lop: ["cloudflare","vultr_singapore","vultr_seoul","linode_singapore"],
    train_test_split: {
      tong_so_dong: 1294,
      so_mau_train: 1035,
      so_mau_test: 259,
      ty_le_test_pct: 20.0
    }
  },

  // ============================================================
  // 5.2 BASELINE  --  nguon: model/tong_hop_ket_qua.py, so_sanh_baseline.py
  // ============================================================
  baselines: {
    khoang_cach: {
      pop_luon_chon: "vultr_singapore",
      logic: "Mo phong GeoDNS truyen thong - luon chon PoP gan nhat ve dia ly co dinh",
      latency_tb_ms: 128.2,
      latency_trung_vi_ms: 56.0
    },
    trung_binh: {
      pop_luon_chon: "linode_singapore",
      logic: "Luon chon PoP co latency trung binh lich su thap nhat tren toan bo du lieu thu thap",
      latency_tb_ms: 70.6,
      latency_trung_vi_ms: 56.0
    }
  },

  // ============================================================
  // 5.3 MO HINH PHAN LOAI (TANG 1)  --  nguon: model/train_tier1.py (chay that)
  // ============================================================
  tier1: {
    ly_do_chon_thuat_toan: "Decision Tree lam baseline ky thuat de doi chieu (de giai thich, huan luyen nhanh), sau do nang cap len Random Forest de kiem tra muc do cai thien va giam overfitting",

    models: [
      {
        name: "Decision Tree",
        accuracy: 0.757,
        latency_tb_ms: 64.7,
        latency_trung_vi_ms: 49.0,
        macro_avg: {precision:0.60, recall:0.79, f1:0.62},
        weighted_avg: {precision:0.76, recall:0.76, f1:0.76},
        per_class: [
          {pop:"cloudflare", precision:0.64, recall:0.55, f1:0.59, support:55},
          {pop:"linode_singapore", precision:0.79, recall:0.75, f1:0.77, support:102},
          {pop:"vultr_seoul", precision:0.17, recall:1.00, f1:0.29, support:1},
          {pop:"vultr_singapore", precision:0.81, recall:0.87, f1:0.84, support:101}
        ],
        confusion_matrix: {
          labels: ["cloudflare","linode_singapore","vultr_seoul","vultr_singapore"],
          matrix: [
            [30, 14, 1, 10],
            [12, 77, 2, 11],
            [0, 0, 1, 0],
            [5, 6, 2, 88]
          ]
        }
      },
      {
        name: "Random Forest",
        accuracy: 0.753,
        latency_tb_ms: 61.7,
        latency_trung_vi_ms: 49.0,
        macro_avg: {precision:0.61, recall:0.80, f1:0.63},
        weighted_avg: {precision:0.76, recall:0.75, f1:0.75},
        per_class: [
          {pop:"cloudflare", precision:0.62, recall:0.60, f1:0.61, support:55},
          {pop:"linode_singapore", precision:0.83, recall:0.73, f1:0.77, support:102},
          {pop:"vultr_seoul", precision:0.20, recall:1.00, f1:0.33, support:1},
          {pop:"vultr_singapore", precision:0.78, recall:0.86, f1:0.82, support:101}
        ],
        confusion_matrix: {
          labels: ["cloudflare","linode_singapore","vultr_seoul","vultr_singapore"],
          matrix: [
            [33, 9, 1, 12],
            [14, 74, 1, 13],
            [0, 0, 1, 0],
            [6, 6, 2, 87]
          ]
        }
      }
    ],

    class_distribution: [
      {pop:"linode_singapore", so_mau:511},
      {pop:"vultr_singapore", so_mau:503},
      {pop:"cloudflare", so_mau:277},
      {pop:"vultr_seoul", so_mau:3}
    ]
  },

  // ============================================================
  // 5.4 PHAT HIEN BAT THUONG VA TU DONG CHUYEN DOI (TANG 2)
  // nguon: model/tier2_anomaly.py, model/dinh_tuyen.py (chay tren toan bo du lieu that)
  // ============================================================
  tier2: {
    phuong_phap: "Isolation Forest VA nguong thong ke dong (trung binh + 3 do lech chuan) - chi kich hoat chuyen doi khi CA HAI cung xac nhan bat thuong",

    so_lan_bao_dong: {
      isolation_forest: 54,
      nguong_thong_ke: 8,
      ca_hai_cung_xac_nhan: 8
    },

    so_lan_chuyen_doi_thuc_te: 8,

    ty_le_chon_duoc_pop_thay_the_tot_hon: "8/8 (100%)",

    switch_count_by_region: [
      {vung:"Bac", isp:"FPT", so_lan:5},
      {vung:"Nam", isp:"VNPT", so_lan:3}
    ],

    pop_hay_bi_phat_hien_loi_nhat: [
      {pop:"linode_singapore", so_lan:3},
      {pop:"vultr_singapore", so_lan:2},
      {pop:"cloudflare", so_lan:2},
      {pop:"vultr_seoul", so_lan:1}
    ],

    toan_bo_8_lan_chuyen_doi: [
      {thoi_diem:"2026-09-14 21:11:03", vung:"Bac", isp:"FPT", pop_cu:"linode_singapore", latency_luc_phat_hien:1327.0, pop_moi:"vultr_singapore", latency_pop_moi:68.0},
      {thoi_diem:"2026-09-15 13:37:00", vung:"Bac", isp:"FPT", pop_cu:"vultr_singapore", latency_luc_phat_hien:499.0, pop_moi:"cloudflare", latency_pop_moi:252.0},
      {thoi_diem:"2026-09-15 13:59:21", vung:"Bac", isp:"FPT", pop_cu:"cloudflare", latency_luc_phat_hien:366.0, pop_moi:"vultr_seoul", latency_pop_moi:333.0},
      {thoi_diem:"2026-09-15 16:01:12", vung:"Bac", isp:"FPT", pop_cu:"vultr_seoul", latency_luc_phat_hien:604.0, pop_moi:"vultr_singapore", latency_pop_moi:233.0},
      {thoi_diem:"2026-09-15 23:35:31", vung:"Bac", isp:"FPT", pop_cu:"vultr_singapore", latency_luc_phat_hien:686.0, pop_moi:"linode_singapore", latency_pop_moi:41.0},
      {thoi_diem:"2026-09-15 08:53:56", vung:"Nam", isp:"VNPT", pop_cu:"linode_singapore", latency_luc_phat_hien:288.0, pop_moi:"cloudflare", latency_pop_moi:129.0},
      {thoi_diem:"2026-09-15 10:32:57", vung:"Nam", isp:"VNPT", pop_cu:"cloudflare", latency_luc_phat_hien:559.0, pop_moi:"linode_singapore", latency_pop_moi:354.0},
      {thoi_diem:"2026-09-15 11:28:17", vung:"Nam", isp:"VNPT", pop_cu:"linode_singapore", latency_luc_phat_hien:654.0, pop_moi:"cloudflare", latency_pop_moi:147.0}
    ],

    log_file: "logs/tier2_log.csv"
  },

  // ============================================================
  // 5.5 KICH BAN MO PHONG SU CO  --  nguon: model/tong_hop_ket_qua.py (chay that)
  // ============================================================
  incident_simulation: {
    co_so_dung_de_dung_hinh: {
      mo_ta: "Trich hinh dang tu dot su co that cua PoP 'cloudflare' (du lieu goc, dong 341-348)",
      he_so_nhan_so_voi_trung_vi_binh_thuong: [0.95, 0.98, 16.13, 0.93, 0.95, 0.91, 0.95, 0.95]
    }
  },

  // ============================================================
  // 5.6 KET QUA TONG HOP  --  nguon: model/tong_hop_ket_qua.py (chay that)
  // ============================================================
  comparison: {
    normal: {
      note: "Tap test, 20% du lieu",
      decision_tree: { vs_khoang_cach: 49.5, vs_trung_binh: 8.4 },
      random_forest: { vs_khoang_cach: 51.9, vs_trung_binh: 12.6 }
    },
    co_su_co: {
      so_kich_ban_mo_phong: 12,
      trung_binh_ca_cua_so: {
        vs_khoang_cach: 1.0, vs_trung_binh: 0.1,
        ghi_chu: "8 luot do/kich ban, gom ca truoc va sau dinh su co"
      },
      chi_tai_dung_luot_dinh: {
        vs_khoang_cach: 0.0, vs_trung_binh: 0.0,
        ghi_chu: "luon la 0% vi ca AI va baseline deu chiu dung 1 lan doc gay ra phat hien - khong the tranh duoc"
      },
      sau_khi_chuyen_doi: {
        vs_khoang_cach: 4.7, vs_trung_binh: 0.5,
        ghi_chu: "day moi la gia tri THAT SU cua Tang 2 - AI da doi PoP, baseline thi khong bao gio doi"
      },
      ty_le_phat_hien_dung_pop_loi_pct: 100.0
    },
    thoi_gian_phan_ung: {
      so_chu_ky_do_can_cho: 0.00,
      do_dai_1_chu_ky_phut: 10.8,
      thoi_gian_xu_ly_thuat_toan_ms: 9.56
    }
  },

  limitations: [
    "Trung-Viettel chi thu thap 6 ngay, duoi moc toi thieu 7 ngay cua de cuong",
    "Nam-VNPT co khoang nghi do giua chung, thuc chat chi ~6.4 ngay du lieu lien tuc dua tren 11 ngay lich",
    "Lop vultr_seoul chi co 3 mau trong toan bo du lieu, gay mat can bang lop nghiem trong (macro F1 thap hon nhieu weighted F1)",
    "So lan chuyen doi thuc te tren du lieu that (8 lan) khac voi so kich ban mo phong dung de danh gia ty le phat hien (12 kich ban) - hai con so nay khong cung mot phep do va khong nen gop chung"
  ]
};