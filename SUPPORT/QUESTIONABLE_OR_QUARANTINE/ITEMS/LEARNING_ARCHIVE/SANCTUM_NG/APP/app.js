(function () {
  const REQUIRED_ACTION_ORDER = [
    "REFRESH_TRUTH_STATE",
    "VALIDATE_TRUTH_STATE",
    "READ_PHASE_REGISTRY",
    "READ_ACTION_REGISTRY",
    "READ_LATEST_REPORT_SUMMARY",
    "CHECK_CONTOUR_STATUS",
    "REGISTER_TASKPACK_SEND",
    "REGISTER_REPORT_BUNDLE_FETCH",
    "DRY_RUN_TASKPACK_SEND",
    "DRY_RUN_REPORT_FETCH",
    "REFRESH_TRANSFER_CONSOLE_VIEW",
    "SEND_TASKPACK_ZIP",
    "FETCH_REPORT_BUNDLE_ZIP",
    "REGISTER_TRANSFER_RESULT",
    "VALIDATE_TRANSFER_REQUEST",
    "DRY_RUN_TRANSFER"
  ];

  const ACTION_LAYER_STATE_MODEL = {
    action: ["ACTION_ALLOWED", "ACTION_DISABLED"],
    result: [
      "ACTION_RESULT_PASS",
      "ACTION_RESULT_WARN",
      "ACTION_RESULT_BLOCK",
      "ACTION_RESULT_PARTIAL"
    ]
  };

  const I18N = {
    en: {
      kicker: "IMPERIUM NEW GENERATION",
      title: "Sanctum Truth Shell V0.1",
      subtitle: "Foundation truth surface with file-backed action layer.",
      labels: {
        task: "Task",
        head: "HEAD",
        mode: "Mode",
        worktree: "Worktree",
        generated: "Generated",
        registryStatus: "Registry Status",
        reportSummaryStatus: "Report Summary",
        resultModelState: "Result Model",
        lastActionStatus: "Last Action Status",
        lastActionPath: "Result Path",
        lastActionSummary: "Result Summary"
      },
      railTitle: "Pipeline Zones",
      warningsTitle: "Known Warnings",
      commTitle: "Communication Gate",
      truthIndexTitle: "Current Truth Index",
      truthIndexLabels: {
        status: "STATUS",
        currentTruthRoot: "CURRENT_TRUTH_ROOT",
        reportStatusIndex: "REPORT_STATUS_INDEX",
        evidenceSourceMap: "EVIDENCE_SOURCE_MAP",
        evidenceMapUnified: "EVIDENCE_MAP_UNIFIED",
        evidenceFreshnessIndex: "EVIDENCE_FRESHNESS_INDEX",
        sync: "SYNC"
      },
      organDialogueTitle: "Organ Dialogue Demo",
      organDialogueLabels: {
        task: "TASK",
        requests: "REQUESTS",
        responses: "RESPONSES",
        warnings: "WARNINGS",
        lastEvent: "LAST_EVENT",
        foundation: "FOUNDATION",
        autonomy: "AUTONOMY"
      },
      organDialogueMissing: "No Organ Dialogue demo data yet.",
      pipelineTitle: "Foundation Pipeline 1-10",
      inspectorTitle: "Phase Inspector",
      inspectorEmpty: "Select a phase to inspect details.",
      inspectorPaths: "Paths",
      inspectorReports: "Report paths",
      inspectorLimits: "Limitations",
      inspectorSnapshot: "JSON snapshot",
      sessionTitle: "Servitor Session View",
      sessionNote: "Read-only timeline from existing NewGen artifacts.",
      sessionLabels: {
        sessionId: "Session",
        task: "Task",
        head: "HEAD",
        branch: "Branch",
        timeline: "Timeline",
        nextStep: "Next Step"
      },
      sessionSourceTitle: "Source Reports",
      sessionEvidenceTitle: "Evidence Summary",
      sessionOrganTitle: "Organ Dialogue",
      sessionActionTitle: "Action Layer",
      sessionTimelineTitle: "Run / Rerun Timeline",
      sessionWarningsTitle: "Session Warnings",
      sessionBoundaryNote: "Foundation-only view. No live autonomous execution claim.",
      sessionNoData: "Session view state is not available yet.",
      ownerQuestionTitle: "Owner Question Gate",
      ownerQuestionNote: "Read-only owner decision queue backed by NewGen files.",
      ownerQuestionLabels: {
        total: "Total",
        open: "Open",
        blocking: "Blocking",
        deferred: "Deferred",
        warnOnly: "Warn-only",
        ownerRequired: "Owner required",
        derivedGate: "Derived Gate",
        nextStep: "Next Step"
      },
      ownerQuestionCardTitle: "Question Cards",
      ownerQuestionWarningsTitle: "Gate Warnings",
      ownerQuestionBoundary: "FOUNDATION_ONLY / NOT LIVE OWNER CHANNEL",
      ownerQuestionNoData: "Owner Question Gate state is not available yet.",
      ownerQuestionNotWired: "Answer channel: NOT_WIRED",
      transferTitle: "Transfer Console",
      transferNote: "Foundation transfer visibility for PC / VM2 / VM3 and allowlisted transfer records.",
      transferLabels: {
        generated: "Generated",
        claimBoundary: "Claim Boundary",
        requests: "Requests",
        results: "Results",
        ledgerEntries: "Ledger Entries",
        contextMix: "Context Mix",
        runnerState: "Runner State",
        shellSafety: "No Arbitrary Shell"
      },
      transferContoursTitle: "Contour Cards",
      transferRequestsTitle: "Latest Requests",
      transferResultsTitle: "Latest Results",
      transferLedgerTitle: "Action Ledger",
      transferSourcesTitle: "Source Refs",
      transferBoundaryNote: "FOUNDATION_ONLY / NO_PRODUCTION_REMOTE_ORCHESTRATION",
      transferRunnerNote: "Transfer action runner state is not available yet.",
      transferNoData: "Transfer Console state is not available yet.",
      actionsTitle: "Action Layer",
      lastActionJsonTitle: "Last Action Result JSON",
      foundationNote: "Foundation-only layer. No production/autonomous claim.",
      worktreeClean: "clean",
      worktreeDirty: "dirty",
      serverConnected: "CONNECTED",
      serverNotConnected: "NOT_CONNECTED",
      serverUnknown: "UNKNOWN",
      serverNotConnectedFile: "ACTION_SERVER_NOT_CONNECTED (file:// mode)",
      serverNotConnectedRuntime: "ACTION_SERVER_NOT_CONNECTED",
      serverConnectedNote: "Local action server is connected.",
      runAction: "Run",
      previewOnly: "Preview only",
      unavailable: "Unavailable",
      running: "RUNNING",
      statusUnknown: "UNKNOWN",
      noResult: "No action result yet.",
      noEvidenceDowngrade: "PASS_WITHOUT_EVIDENCE_DOWNGRADED_TO_WARN"
    },
    ru: {
      kicker: "IMPERIUM НОВОЕ ПОКОЛЕНИЕ",
      title: "Sanctum Truth Shell V0.1",
      subtitle: "Foundation truth surface with file-backed action layer.",
      labels: {
        task: "Задача",
        head: "HEAD",
        mode: "Режим",
        worktree: "Дерево",
        generated: "Сгенерировано",
        registryStatus: "Статус реестра",
        reportSummaryStatus: "Сводка отчётов",
        resultModelState: "Модель результата",
        lastActionStatus: "Статус последнего действия",
        lastActionPath: "Путь результата",
        lastActionSummary: "Сводка результата"
      },
      railTitle: "Зоны контура",
      warningsTitle: "Известные предупреждения",
      commTitle: "Гейт коммуникации",
      truthIndexTitle: "Индекс текущей правды",
      truthIndexLabels: {
        status: "СТАТУС",
        currentTruthRoot: "CURRENT_TRUTH_ROOT",
        reportStatusIndex: "REPORT_STATUS_INDEX",
        evidenceSourceMap: "EVIDENCE_SOURCE_MAP",
        evidenceMapUnified: "EVIDENCE_MAP_UNIFIED",
        evidenceFreshnessIndex: "EVIDENCE_FRESHNESS_INDEX",
        sync: "СИНХРОН"
      },
      organDialogueTitle: "Демо Диалога Органов",
      organDialogueLabels: {
        task: "ДЕМО_ЗАДАЧА",
        requests: "ЗАПРОСЫ",
        responses: "ОТВЕТЫ",
        warnings: "ПРЕДУПРЕЖДЕНИЯ",
        lastEvent: "ПОСЛЕДНЕЕ_СОБЫТИЕ",
        foundation: "ГРАНИЦА",
        autonomy: "АВТОНОМИЯ"
      },
      organDialogueMissing: "Пока нет данных демо-диалога органов.",
      pipelineTitle: "Фундаментальный конвейер 1-10",
      inspectorTitle: "Инспектор фазы",
      inspectorEmpty: "Выберите фазу для просмотра деталей.",
      inspectorPaths: "Пути",
      inspectorReports: "Пути отчётов",
      inspectorLimits: "Ограничения",
      inspectorSnapshot: "JSON-снимок",
      sessionTitle: "Servitor Session View",
      sessionNote: "Read-only timeline из существующих NewGen артефактов.",
      sessionLabels: {
        sessionId: "Сессия",
        task: "Задача",
        head: "HEAD",
        branch: "Ветка",
        timeline: "Таймлайн",
        nextStep: "Следующий шаг"
      },
      sessionSourceTitle: "Источник отчётов",
      sessionEvidenceTitle: "Сводка evidence",
      sessionOrganTitle: "Диалог Органов",
      sessionActionTitle: "Слой действий",
      sessionTimelineTitle: "Таймлайн Run / Rerun",
      sessionWarningsTitle: "Предупреждения сессии",
      sessionBoundaryNote: "Только foundation-view. Без claim live autonomous execution.",
      sessionNoData: "Состояние Session View пока недоступно.",
      ownerQuestionTitle: "Owner Question Gate",
      ownerQuestionNote: "Read-only очередь Owner-решений на file-backed базе NewGen.",
      ownerQuestionLabels: {
        total: "Всего",
        open: "Открыто",
        blocking: "Блокирующие",
        deferred: "Отложено",
        warnOnly: "Warn-only",
        ownerRequired: "Требуют Owner",
        derivedGate: "Производный гейт",
        nextStep: "Следующий шаг"
      },
      ownerQuestionCardTitle: "Карточки вопросов",
      ownerQuestionWarningsTitle: "Предупреждения гейта",
      ownerQuestionBoundary: "FOUNDATION_ONLY / NOT LIVE OWNER CHANNEL",
      ownerQuestionNoData: "Состояние Owner Question Gate пока недоступно.",
      ownerQuestionNotWired: "Канал ответа: NOT_WIRED",
      transferTitle: "Transfer Console",
      transferNote: "Foundation-видимость PC / VM2 / VM3 и allowlisted transfer-записей.",
      transferLabels: {
        generated: "Сгенерировано",
        claimBoundary: "Граница claim",
        requests: "Запросы",
        results: "Результаты",
        ledgerEntries: "Записи ledger",
        contextMix: "Context Mix",
        runnerState: "Состояние runner",
        shellSafety: "Без arbitrary shell"
      },
      transferContoursTitle: "Карточки контуров",
      transferRequestsTitle: "Последние запросы",
      transferResultsTitle: "Последние результаты",
      transferLedgerTitle: "Action Ledger",
      transferSourcesTitle: "Source Refs",
      transferBoundaryNote: "FOUNDATION_ONLY / NO_PRODUCTION_REMOTE_ORCHESTRATION",
      transferRunnerNote: "Состояние transfer action runner пока недоступно.",
      transferNoData: "Состояние Transfer Console пока недоступно.",
      actionsTitle: "Слой действий",
      lastActionJsonTitle: "JSON последнего результата",
      foundationNote: "Только foundation-слой. Без production/autonomous claim.",
      worktreeClean: "чисто",
      worktreeDirty: "грязно",
      serverConnected: "CONNECTED",
      serverNotConnected: "NOT_CONNECTED",
      serverUnknown: "UNKNOWN",
      serverNotConnectedFile: "ACTION_SERVER_NOT_CONNECTED (file:// режим)",
      serverNotConnectedRuntime: "ACTION_SERVER_NOT_CONNECTED",
      serverConnectedNote: "Локальный action server подключен.",
      runAction: "Запустить",
      previewOnly: "Только превью",
      unavailable: "Недоступно",
      running: "ВЫПОЛНЯЕТСЯ",
      statusUnknown: "UNKNOWN",
      noResult: "Результат действия пока отсутствует.",
      noEvidenceDowngrade: "PASS без evidence понижен до WARN"
    }
  };

  const FALLBACK_STATE = {
    schema_id: "SANCTUM_NG_STATE_V0_1",
    task_id: "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1",
    mode: "ACTION_LAYER_FOUNDATION_ONLY",
    generated_at_utc: "FALLBACK",
    git: {
      head: "UNKNOWN",
      branch: "UNKNOWN",
      worktree_dirty: false
    },
    warnings: ["FALLBACK_STATE_ACTIVE"],
    communication_gate: {
      LIVE_LANGUAGE_COMPLIANCE: "RUSSIAN_OWNER_PROGRESS_REQUIRED",
      FINAL_REPORT_LANGUAGE: "RUSSIAN_REQUIRED",
      TECHNICAL_ARTIFACT_LANGUAGE: "ENGLISH_ALLOWED",
      AUTHORITY_SOURCE: [
        "IMPERIUM_NEW_GENERATION/AUTHORITY_DRAFTS/OFFICIO_LIVE_COMMUNICATION_ENFORCEMENT_V0_1.md"
      ],
      STATUS: "WARN_FOUNDATION_ONLY",
      KNOWN_LIMITATION: "Fallback state is active; runtime hard-block is not claimed."
    },
    current_truth_index: {
      current_truth_root_path: "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json",
      report_status_index_path: "IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_INDEX_V0_1.json",
      evidence_source_map_path: "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_SOURCE_MAP_V0_1.json",
      evidence_map_unified_path: "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_MAP_UNIFIED_V0_1.json",
      evidence_freshness_index_path: "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_FRESHNESS_INDEX_V0_1.json",
      status: "UNKNOWN",
      last_sync_utc: "UNKNOWN"
    },
    organ_dialogue_demo: {
      task_id: "TASK-DEMO-ORGAN-DIALOGUE-V0_1",
      thread_id: "THREAD-TASK-DEMO-ORGAN-DIALOGUE-V0_1",
      request_count: 0,
      response_count: 0,
      warnings_count: 0,
      last_event: "NOT_READY",
      foundation_only_label: "FOUNDATION_ONLY",
      no_live_autonomy_label: "NO_LIVE_AUTONOMY"
    },
    phases: [
      { phase_no: 1, name: "Architecture", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 2, name: "Organ Packets", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 3, name: "Task Kernel", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 4, name: "Astronomicon", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 5, name: "Authority Gates", status: "WARN", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 6, name: "Servitor Loop", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 7, name: "Evidence Binder", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 8, name: "Visual Brain", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 9, name: "Skill Growth", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] },
      { phase_no: 10, name: "Tool Admission", status: "FOUNDATION", summary: "Fallback snapshot.", evidence_refs: ["FALLBACK"], paths: [], report_paths: [], limitations: ["State API unavailable."] }
    ]
  };

  const FALLBACK_ACTIONS = [
    {
      action_id: "REFRESH_TRUTH_STATE",
      title: "Refresh Sanctum Truth State",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_LOCAL_SCRIPT_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "VALIDATE_TRUTH_STATE",
      title: "Validate Sanctum Truth State",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_LOCAL_SCRIPT_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "READ_PHASE_REGISTRY",
      title: "Read Phase Registry",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_READ_FIXED_PATH",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "READ_ACTION_REGISTRY",
      title: "Read Action Registry",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_READ_FIXED_PATH",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "READ_LATEST_REPORT_SUMMARY",
      title: "Read Latest Report Summary",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_READ_FIXED_REPORT_SET",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "CHECK_CONTOUR_STATUS",
      title: "Check Transfer Contours",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_LOCAL_PROBE_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "REGISTER_TASKPACK_SEND",
      title: "Register Taskpack Send",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_FILE_BACKED_REGISTRATION",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "REGISTER_REPORT_BUNDLE_FETCH",
      title: "Register Report Fetch",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_FILE_BACKED_REGISTRATION",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "DRY_RUN_TASKPACK_SEND",
      title: "Dry Run Taskpack Send",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_DRY_RUN_RECORD_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "DRY_RUN_REPORT_FETCH",
      title: "Dry Run Report Fetch",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_DRY_RUN_RECORD_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "REFRESH_TRANSFER_CONSOLE_VIEW",
      title: "Refresh Transfer Console View",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_LOCAL_SCRIPT_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "SEND_TASKPACK_ZIP",
      title: "Send Taskpack ZIP",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_TRANSFER_ALLOWLIST_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "FETCH_REPORT_BUNDLE_ZIP",
      title: "Fetch Report Bundle ZIP",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_TRANSFER_ALLOWLIST_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "REGISTER_TRANSFER_RESULT",
      title: "Register Transfer Result",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_FILE_BACKED_REGISTRATION",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "VALIDATE_TRANSFER_REQUEST",
      title: "Validate Transfer Request",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_REQUEST_VALIDATION_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    },
    {
      action_id: "DRY_RUN_TRANSFER",
      title: "Dry Run Transfer",
      description: "Requires local action server.",
      status: "NOT_WIRED",
      safety_level: "SAFE_DRY_RUN_RECORD_ONLY",
      allowed_commands: [],
      allowed_paths: [],
      forbidden_paths: ["*"],
      writes_files: [],
      evidence_refs: [],
      known_limitations: ["ACTION_SERVER_NOT_CONNECTED"]
    }
  ];

  const FALLBACK_OWNER_QUESTION_GATE = {
    schema_id: "OWNER_QUESTION_GATE_STATE_V0_1",
    task_id: "TASK-20260523-NEWGEN-SANCTUM-OWNER-QUESTION-GATE-VM2-V0_1",
    mode: "FOUNDATION_READ_ONLY_OWNER_QUESTION_GATE",
    generated_at_utc: "FALLBACK",
    truth_flags: {
      read_only: true,
      foundation_only: true,
      live_owner_channel: false,
      owner_answer_write_path: false,
      production_ready: false
    },
    summary: {
      total_questions: 0,
      open_count: 0,
      blocking_count: 0,
      deferred_count: 0,
      warn_only_count: 0,
      answered_count: 0,
      stale_count: 0,
      foundation_sample_count: 0,
      owner_answer_required_count: 0,
      derived_gate_status: "FOUNDATION_SAMPLE_ONLY"
    },
    questions: [],
    events: [],
    warnings: ["OWNER_QUESTION_GATE_STATE_NOT_LOADED"],
    boundary_note: "FOUNDATION_ONLY / NOT LIVE OWNER CHANNEL",
    next_required_step: "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM2-OR-VM3-V0_1"
  };

  const FALLBACK_TRANSFER_CONSOLE_VIEW = {
    schema_id: "TRANSFER_CONSOLE_VIEW_STATE_V0_1",
    task_id: "TASK-20260523-NEWGEN-SANCTUM-TRANSFER-CONSOLE-VM3-V0_1",
    generated_at_utc: "FALLBACK",
    claim_boundary: "FOUNDATION_ONLY",
    contour_cards: [
      {
        contour_id: "PC",
        display_name: "PC",
        role: "control_contour",
        status: "NOT_CONFIGURED",
        status_reason: "No bounded VM3-side route is configured.",
        route_config_status: "NOT_CONFIGURED",
        last_probe_receipt_ref: null,
        last_updated_utc: "UNKNOWN",
        claim_boundary: "FOUNDATION_ONLY"
      },
      {
        contour_id: "VM2",
        display_name: "VM2",
        role: "executor_contour",
        status: "UNKNOWN",
        status_reason: "No fresh bounded probe receipt exists.",
        route_config_status: "CONFIGURED_NOT_VERIFIED",
        last_probe_receipt_ref: null,
        last_updated_utc: "UNKNOWN",
        claim_boundary: "FOUNDATION_ONLY"
      },
      {
        contour_id: "VM3",
        display_name: "VM3",
        role: "executor_contour",
        status: "UNKNOWN",
        status_reason: "No fresh bounded probe receipt exists.",
        route_config_status: "CONFIGURED",
        last_probe_receipt_ref: null,
        last_updated_utc: "UNKNOWN",
        claim_boundary: "FOUNDATION_ONLY"
      }
    ],
    latest_requests: [],
    latest_results: [],
    action_ledger: [],
    transfer_routes: [],
    source_refs: [],
    context_source_mix: {
      taskpack_percent: 70,
      existing_newgen_repo_percent: 22,
      owner_handoff_percent: 5,
      organ_registry_percent: 2,
      servitor_inference_percent: 1,
      external_local_private_percent: 0
    },
    truth_labels: [
      "FOUNDATION_ONLY",
      "NO_PRODUCTION_REMOTE_ORCHESTRATION",
      "NO_ARBITRARY_SHELL",
      "NO_FAKE_GREEN"
    ],
    action_runner_state: {
      schema_id: "TRANSFER_ACTION_RUNNER_STATE_V0_1",
      generated_at_utc: "FALLBACK",
      claim_boundary: "FOUNDATION_ONLY",
      no_arbitrary_shell_confirmed: true,
      supported_action_types: [
        "SEND_TASKPACK_ZIP",
        "FETCH_REPORT_BUNDLE_ZIP",
        "REGISTER_TRANSFER_RESULT",
        "VALIDATE_TRANSFER_REQUEST",
        "DRY_RUN_TRANSFER"
      ],
      allowed_contours: ["PC", "VM2", "VM3"],
      safe_target_roots: {},
      latest_action_requests: [],
      latest_action_results: [],
      latest_runner_ledger: [],
      last_action: {
        action_id: "NOT_READY",
        request_ref: null,
        result_ref: null
      },
      status_labels: [
        "DRY_RUN_OK",
        "SENT",
        "FETCHED",
        "CONFIRMED",
        "REGISTERED",
        "FAILED",
        "BLOCKED",
        "NOT_READY"
      ],
      known_limitations: ["ACTION_RUNNER_STATE_NOT_LOADED"]
    }
  };

  const state = {
    lang: "en",
    data: null,
    actions: [],
    selectedPhaseNo: null,
    serverStatus: "UNKNOWN",
    connectionNote: "",
    lastActionResult: null,
    registryStatus: "UNKNOWN",
    reportSummaryState: "UNKNOWN",
    reportSummaryReason: "-",
    lastActionModelState: "ACTION_RESULT_WARN",
    actionLayerStateModel: null,
    sessionView: null,
    ownerQuestionGate: null,
    transferConsoleView: null
  };

  function byOrder(actions) {
    const order = new Map(REQUIRED_ACTION_ORDER.map((id, idx) => [id, idx]));
    return actions.slice().sort((a, b) => {
      const ax = order.has(a.action_id) ? order.get(a.action_id) : 999;
      const bx = order.has(b.action_id) ? order.get(b.action_id) : 999;
      return ax - bx;
    });
  }

  function normalizeData(rawData) {
    const data = rawData && typeof rawData === "object" ? rawData : FALLBACK_STATE;
    const phases = Array.isArray(data.phases) ? data.phases.slice() : [];
    phases.sort((a, b) => Number(a.phase_no) - Number(b.phase_no));

    const warnings = Array.isArray(data.warnings) ? data.warnings.slice() : [];

    phases.forEach((phase) => {
      const refs = Array.isArray(phase.evidence_refs) ? phase.evidence_refs : [];
      if (phase.status === "PROVED" && refs.length === 0) {
        phase.status = "WARN";
        warnings.push(`PHASE_${phase.phase_no}_PROVED_WITHOUT_EVIDENCE_DOWNGRADED`);
      }
    });

    if (!data.communication_gate || typeof data.communication_gate !== "object") {
      data.communication_gate = { ...FALLBACK_STATE.communication_gate };
      warnings.push("COMMUNICATION_GATE_FALLBACK_ACTIVE");
    }

    data.phases = phases;
    data.warnings = warnings;
    return data;
  }

  function normalizeActions(rawActions) {
    const source = Array.isArray(rawActions) ? rawActions : FALLBACK_ACTIONS;
    const actions = source
      .filter((item) => item && typeof item === "object")
      .map((item) => ({
        action_id: String(item.action_id || "UNKNOWN_ACTION"),
        title: String(item.title || item.action_id || "Unknown Action"),
        description: String(item.description || ""),
        status: String(item.status || "NOT_WIRED"),
        availability_state: String(item.availability_state || "ACTION_DISABLED"),
        safety_level: String(item.safety_level || "UNKNOWN"),
        allowed_commands: Array.isArray(item.allowed_commands) ? item.allowed_commands : [],
        allowed_paths: Array.isArray(item.allowed_paths) ? item.allowed_paths : [],
        forbidden_paths: Array.isArray(item.forbidden_paths) ? item.forbidden_paths : [],
        writes_files: Array.isArray(item.writes_files) ? item.writes_files : [],
        evidence_refs: Array.isArray(item.evidence_refs) ? item.evidence_refs : [],
        known_limitations: Array.isArray(item.known_limitations) ? item.known_limitations : []
      }));

    return byOrder(actions);
  }

  function normalizeOwnerQuestionGate(rawGate) {
    const gate = rawGate && typeof rawGate === "object" ? rawGate : FALLBACK_OWNER_QUESTION_GATE;
    const out = { ...FALLBACK_OWNER_QUESTION_GATE, ...gate };
    const summary = gate.summary && typeof gate.summary === "object" ? gate.summary : {};
    out.summary = { ...FALLBACK_OWNER_QUESTION_GATE.summary, ...summary };
    out.questions = Array.isArray(gate.questions) ? gate.questions.filter((q) => q && typeof q === "object") : [];
    out.warnings = Array.isArray(gate.warnings) ? gate.warnings.map((w) => String(w)) : [];
    return out;
  }

  function normalizeTransferConsole(rawView) {
    const view = rawView && typeof rawView === "object" ? rawView : FALLBACK_TRANSFER_CONSOLE_VIEW;
    const out = { ...FALLBACK_TRANSFER_CONSOLE_VIEW, ...view };
    out.contour_cards = Array.isArray(view.contour_cards)
      ? view.contour_cards.filter((item) => item && typeof item === "object")
      : FALLBACK_TRANSFER_CONSOLE_VIEW.contour_cards;
    out.latest_requests = Array.isArray(view.latest_requests)
      ? view.latest_requests.filter((item) => item && typeof item === "object")
      : [];
    out.latest_results = Array.isArray(view.latest_results)
      ? view.latest_results.filter((item) => item && typeof item === "object")
      : [];
    out.action_ledger = Array.isArray(view.action_ledger)
      ? view.action_ledger.filter((item) => item && typeof item === "object")
      : [];
    out.transfer_routes = Array.isArray(view.transfer_routes)
      ? view.transfer_routes.filter((item) => item && typeof item === "object")
      : [];
    out.source_refs = Array.isArray(view.source_refs) ? view.source_refs.map((item) => String(item)) : [];
    const mix = view.context_source_mix && typeof view.context_source_mix === "object"
      ? view.context_source_mix
      : {};
    out.context_source_mix = {
      ...FALLBACK_TRANSFER_CONSOLE_VIEW.context_source_mix,
      ...mix
    };
    out.truth_labels = Array.isArray(view.truth_labels) ? view.truth_labels.map((item) => String(item)) : [];
    const runnerState = view.action_runner_state && typeof view.action_runner_state === "object"
      ? view.action_runner_state
      : {};
    out.action_runner_state = {
      ...FALLBACK_TRANSFER_CONSOLE_VIEW.action_runner_state,
      ...runnerState,
      supported_action_types: Array.isArray(runnerState.supported_action_types)
        ? runnerState.supported_action_types.map((item) => String(item))
        : FALLBACK_TRANSFER_CONSOLE_VIEW.action_runner_state.supported_action_types,
      allowed_contours: Array.isArray(runnerState.allowed_contours)
        ? runnerState.allowed_contours.map((item) => String(item))
        : FALLBACK_TRANSFER_CONSOLE_VIEW.action_runner_state.allowed_contours,
      latest_action_requests: Array.isArray(runnerState.latest_action_requests)
        ? runnerState.latest_action_requests.filter((item) => item && typeof item === "object")
        : [],
      latest_action_results: Array.isArray(runnerState.latest_action_results)
        ? runnerState.latest_action_results.filter((item) => item && typeof item === "object")
        : [],
      latest_runner_ledger: Array.isArray(runnerState.latest_runner_ledger)
        ? runnerState.latest_runner_ledger.filter((item) => item && typeof item === "object")
        : [],
      known_limitations: Array.isArray(runnerState.known_limitations)
        ? runnerState.known_limitations.map((item) => String(item))
        : []
    };
    return out;
  }

  function applyReportSummary(summaryPayload) {
    const payload = summaryPayload && typeof summaryPayload === "object" ? summaryPayload : {};
    const inner = payload.payload && typeof payload.payload === "object" ? payload.payload : {};
    state.reportSummaryState = String(inner.summary_state || "UNKNOWN");
    state.reportSummaryReason = String(inner.reason || "-");
  }

  function applyLatestActionResult(resultPayload) {
    if (!resultPayload || typeof resultPayload !== "object") {
      return;
    }
    state.lastActionResult = resultPayload;
    const model = resultPayload.state_model && typeof resultPayload.state_model === "object" ? resultPayload.state_model : {};
    state.lastActionModelState = String(model.result_state || "ACTION_RESULT_WARN");

    if (String(resultPayload.action_id || "") === "READ_LATEST_REPORT_SUMMARY") {
      applyReportSummary(resultPayload);
    }
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = text;
    }
  }

  function setStatusValue(id, value) {
    const el = document.getElementById(id);
    if (!el) {
      return;
    }
    const text = String(value || "UNKNOWN");
    el.textContent = text;
    el.className = `status-pill ${statusClass(text)}`;
  }

  function statusClass(status) {
    return `status-${String(status || "").toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
  }

  function setLabels() {
    const t = I18N[state.lang];
    setText("app-kicker", t.kicker);
    setText("app-title", t.title);
    setText("app-subtitle", t.subtitle);

    setText("label-task", t.labels.task);
    setText("label-head", t.labels.head);
    setText("label-mode", t.labels.mode);
    setText("label-worktree", t.labels.worktree);
    setText("label-generated", t.labels.generated);

    setText("rail-title", t.railTitle);
    setText("warnings-title", t.warningsTitle);
    setText("comm-title", t.commTitle);
    setText("truth-index-title", t.truthIndexTitle);
    setText("organ-dialogue-title", t.organDialogueTitle);
    setText("pipeline-title", t.pipelineTitle);

    setText("inspector-title", t.inspectorTitle);
    setText("inspector-empty", t.inspectorEmpty);
    setText("inspector-paths-label", t.inspectorPaths);
    setText("inspector-reports-label", t.inspectorReports);
    setText("inspector-limits-label", t.inspectorLimits);
    setText("inspector-snapshot-label", t.inspectorSnapshot);

    setText("session-title", t.sessionTitle);
    setText("session-note", t.sessionNote);
    setText("label-session-id", t.sessionLabels.sessionId);
    setText("label-session-task", t.sessionLabels.task);
    setText("label-session-head", t.sessionLabels.head);
    setText("label-session-branch", t.sessionLabels.branch);
    setText("label-session-timeline", t.sessionLabels.timeline);
    setText("label-session-next", t.sessionLabels.nextStep);
    setText("session-source-title", t.sessionSourceTitle);
    setText("session-evidence-title", t.sessionEvidenceTitle);
    setText("session-organ-title", t.sessionOrganTitle);
    setText("session-action-title", t.sessionActionTitle);
    setText("session-timeline-title", t.sessionTimelineTitle);
    setText("session-warnings-title", t.sessionWarningsTitle);
    setText("session-boundary-note", t.sessionBoundaryNote);

    setText("owner-questions-title", t.ownerQuestionTitle);
    setText("owner-questions-note", t.ownerQuestionNote);
    setText("label-owner-total", t.ownerQuestionLabels.total);
    setText("label-owner-open", t.ownerQuestionLabels.open);
    setText("label-owner-blocking", t.ownerQuestionLabels.blocking);
    setText("label-owner-deferred", t.ownerQuestionLabels.deferred);
    setText("label-owner-warn", t.ownerQuestionLabels.warnOnly);
    setText("label-owner-required", t.ownerQuestionLabels.ownerRequired);
    setText("label-owner-derived", t.ownerQuestionLabels.derivedGate);
    setText("label-owner-next", t.ownerQuestionLabels.nextStep);
    setText("owner-question-card-title", t.ownerQuestionCardTitle);
    setText("owner-question-warnings-title", t.ownerQuestionWarningsTitle);
    setText("owner-boundary-note", t.ownerQuestionBoundary);

    setText("transfer-title", t.transferTitle);
    setText("transfer-note", t.transferNote);
    setText("label-transfer-generated", t.transferLabels.generated);
    setText("label-transfer-boundary", t.transferLabels.claimBoundary);
    setText("label-transfer-requests", t.transferLabels.requests);
    setText("label-transfer-results", t.transferLabels.results);
    setText("label-transfer-ledger", t.transferLabels.ledgerEntries);
    setText("label-transfer-context", t.transferLabels.contextMix);
    setText("label-transfer-runner", t.transferLabels.runnerState);
    setText("label-transfer-shell", t.transferLabels.shellSafety);
    setText("transfer-contours-title", t.transferContoursTitle);
    setText("transfer-requests-title", t.transferRequestsTitle);
    setText("transfer-results-title", t.transferResultsTitle);
    setText("transfer-ledger-title", t.transferLedgerTitle);
    setText("transfer-sources-title", t.transferSourcesTitle);
    setText("transfer-runner-note", t.transferRunnerNote);
    setText("transfer-boundary-note", t.transferBoundaryNote);

    setText("actions-title", t.actionsTitle);
    setText("label-registry-status", t.labels.registryStatus);
    setText("label-report-summary-status", t.labels.reportSummaryStatus);
    setText("label-result-model-state", t.labels.resultModelState);
    setText("label-last-action-status", t.labels.lastActionStatus);
    setText("label-last-action-path", t.labels.lastActionPath);
    setText("label-last-action-summary", t.labels.lastActionSummary);
    setText("last-action-json-title", t.lastActionJsonTitle);
    setText("foundation-note", t.foundationNote);

    const langBtn = document.getElementById("lang-toggle");
    if (langBtn) {
      langBtn.textContent = state.lang === "en" ? "RU" : "EN";
    }
  }

  function renderTruthBar() {
    const t = I18N[state.lang];
    const data = state.data;
    const git = data.git || {};

    setText("truth-task", data.task_id || "-");
    setText("truth-head", git.head || "-");
    setText("truth-mode", data.mode || "-");
    setText("truth-worktree", git.worktree_dirty ? t.worktreeDirty : t.worktreeClean);
    setText("truth-generated", data.generated_at_utc || "-");
  }

  function renderRail() {
    const rail = document.getElementById("phase-rail");
    rail.innerHTML = "";

    state.data.phases.forEach((phase) => {
      const li = document.createElement("li");
      li.textContent = `${phase.phase_no}. ${phase.name}`;
      rail.appendChild(li);
    });

    const warnings = document.getElementById("warnings-list");
    warnings.innerHTML = "";
    (state.data.warnings || []).forEach((warning) => {
      const li = document.createElement("li");
      li.textContent = warning;
      warnings.appendChild(li);
    });
  }

  function renderPipeline() {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    state.data.phases.forEach((phase) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "phase-card";
      card.innerHTML = `
        <div class="phase-card__top">
          <span class="phase-name">${phase.phase_no}. ${phase.name}</span>
          <span class="status-pill ${statusClass(phase.status)}">${phase.status}</span>
        </div>
        <p class="phase-summary">${phase.summary || ""}</p>
      `;
      card.addEventListener("click", function () {
        state.selectedPhaseNo = phase.phase_no;
        renderInspector();
      });
      list.appendChild(card);
    });
  }

  function renderCommunicationGate() {
    const node = document.getElementById("comm-gate-list");
    node.innerHTML = "";

    const gate = state.data.communication_gate || {};
    const ordered = [
      "STATUS",
      "LIVE_LANGUAGE_COMPLIANCE",
      "FINAL_REPORT_LANGUAGE",
      "TECHNICAL_ARTIFACT_LANGUAGE",
      "KNOWN_LIMITATION"
    ];

    ordered.forEach((key) => {
      const li = document.createElement("li");
      li.textContent = `${key}: ${String(gate[key] || "-")}`;
      node.appendChild(li);
    });

    const sources = Array.isArray(gate.AUTHORITY_SOURCE) ? gate.AUTHORITY_SOURCE : [];
    if (sources.length > 0) {
      const li = document.createElement("li");
      li.textContent = `AUTHORITY_SOURCE: ${sources.join(" | ")}`;
      node.appendChild(li);
    }
  }

  function renderTruthIndex() {
    const t = I18N[state.lang];
    const data = state.data || {};
    const truthIndex = data.current_truth_index && typeof data.current_truth_index === "object"
      ? data.current_truth_index
      : {};

    setText("truth-root-status", `${t.truthIndexLabels.status}: ${String(truthIndex.status || "-")}`);
    setText(
      "truth-root-path",
      `${t.truthIndexLabels.currentTruthRoot}: ${String(truthIndex.current_truth_root_path || "-")}`
    );
    setText(
      "report-index-path",
      `${t.truthIndexLabels.reportStatusIndex}: ${String(truthIndex.report_status_index_path || "-")}`
    );
    setText(
      "evidence-map-path",
      `${t.truthIndexLabels.evidenceSourceMap}: ${String(truthIndex.evidence_source_map_path || "-")}`
    );
    setText(
      "evidence-map-unified-path",
      `${t.truthIndexLabels.evidenceMapUnified}: ${String(truthIndex.evidence_map_unified_path || "-")}`
    );
    setText(
      "freshness-index-path",
      `${t.truthIndexLabels.evidenceFreshnessIndex}: ${String(truthIndex.evidence_freshness_index_path || "-")}`
    );
    setText("truth-sync-utc", `${t.truthIndexLabels.sync}: ${String(truthIndex.last_sync_utc || "-")}`);
  }

  function renderOrganDialogueDemo() {
    const t = I18N[state.lang];
    const data = state.data || {};
    const labels = t.organDialogueLabels;
    const demo = data.organ_dialogue_demo && typeof data.organ_dialogue_demo === "object"
      ? data.organ_dialogue_demo
      : null;

    if (!demo) {
      setText("organ-dialogue-task", `${labels.task}: ${t.organDialogueMissing}`);
      setText("organ-dialogue-requests", `${labels.requests}: -`);
      setText("organ-dialogue-responses", `${labels.responses}: -`);
      setText("organ-dialogue-warnings", `${labels.warnings}: -`);
      setText("organ-dialogue-last-event", `${labels.lastEvent}: -`);
      setText("organ-dialogue-foundation", `${labels.foundation}: -`);
      setText("organ-dialogue-autonomy", `${labels.autonomy}: -`);
      return;
    }

    setText("organ-dialogue-task", `${labels.task}: ${String(demo.task_id || "-")}`);
    setText("organ-dialogue-requests", `${labels.requests}: ${String(demo.request_count ?? "-")}`);
    setText("organ-dialogue-responses", `${labels.responses}: ${String(demo.response_count ?? "-")}`);
    setText("organ-dialogue-warnings", `${labels.warnings}: ${String(demo.warnings_count ?? "-")}`);
    setText("organ-dialogue-last-event", `${labels.lastEvent}: ${String(demo.last_event || "-")}`);
    setText("organ-dialogue-foundation", `${labels.foundation}: ${String(demo.foundation_only_label || "FOUNDATION_ONLY")}`);
    setText("organ-dialogue-autonomy", `${labels.autonomy}: ${String(demo.no_live_autonomy_label || "NO_LIVE_AUTONOMY")}`);
  }

  function renderSessionLines(id, lines) {
    const node = document.getElementById(id);
    node.innerHTML = "";

    if (!Array.isArray(lines) || lines.length === 0) {
      const li = document.createElement("li");
      li.textContent = "-";
      node.appendChild(li);
      return;
    }

    lines.forEach((line) => {
      const li = document.createElement("li");
      li.textContent = String(line);
      node.appendChild(li);
    });
  }

  function renderServitorSessionView() {
    const t = I18N[state.lang];
    const session = state.sessionView;
    const noData = !session || typeof session !== "object";

    if (noData) {
      setStatusValue("session-status-pill", "NOT_READY");
      setText("session-id", "-");
      setText("session-task", "-");
      setText("session-head", "-");
      setText("session-branch", "-");
      setText("session-timeline-summary", t.sessionNoData);
      setText("session-next-step", "-");
      renderSessionLines("session-source-list", []);
      renderSessionLines("session-evidence-list", []);
      renderSessionLines("session-organ-list", []);
      renderSessionLines("session-action-list", []);
      renderSessionLines("session-warnings-list", []);
      const timelineNode = document.getElementById("session-timeline-list");
      timelineNode.innerHTML = "";
      const placeholder = document.createElement("p");
      placeholder.className = "placeholder";
      placeholder.textContent = t.sessionNoData;
      timelineNode.appendChild(placeholder);
      return;
    }

    const sessionStatus = String(session.session_status || "FOUNDATION_ONLY");
    setStatusValue("session-status-pill", sessionStatus);

    const sessionMeta = session.session || {};
    const timelineSummary = session.timeline && session.timeline.summary ? session.timeline.summary : {};
    setText("session-id", String(sessionMeta.session_id || "-"));
    setText("session-task", String(sessionMeta.view_task_id || session.task_id || "-"));
    setText("session-head", String(sessionMeta.current_head || "-"));
    setText("session-branch", String(sessionMeta.branch || "-"));
    setText(
      "session-timeline-summary",
      `events=${String(timelineSummary.total_events || 0)} run=${String(timelineSummary.run_events || 0)} rerun=${String(timelineSummary.rerun_events || 0)}`
    );
    setText("session-next-step", String(session.next_required_step || "-"));

    const sourceReports = session.source_reports && typeof session.source_reports === "object"
      ? session.source_reports
      : {};
    const sourceLines = Object.keys(sourceReports).sort().map((key) => {
      const entry = sourceReports[key] || {};
      return `${key}: ${String(entry.status || "UNKNOWN")} :: ${String(entry.report_dir || "-")}`;
    });
    renderSessionLines("session-source-list", sourceLines);

    const evidence = session.evidence_summary && typeof session.evidence_summary === "object"
      ? session.evidence_summary
      : {};
    const critical = Array.isArray(evidence.critical_refs) ? evidence.critical_refs : [];
    const evidenceLines = [
      `records=${String(evidence.evidence_record_count || 0)}`,
      `report_entries=${String(evidence.report_entry_count || 0)}`,
      `map=${String(evidence.evidence_map_unified_path || "-")}`,
      `index=${String(evidence.report_status_index_path || "-")}`,
      ...critical.slice(0, 4).map((item) => `ref:${String(item)}`),
    ];
    renderSessionLines("session-evidence-list", evidenceLines);

    const organ = session.organ_dialogue && typeof session.organ_dialogue === "object"
      ? session.organ_dialogue
      : {};
    const organLines = [
      `task=${String(organ.task_id || "-")}`,
      `thread=${String(organ.thread_id || "-")}`,
      `requests=${String(organ.request_count ?? "-")} responses=${String(organ.response_count ?? "-")}`,
      `warnings=${String(organ.warnings_count ?? "-")} last=${String(organ.last_event || "-")}`,
      `live_autonomy=${String(organ.live_autonomy ?? "-")}`,
    ];
    renderSessionLines("session-organ-list", organLines);

    const action = session.action_layer && typeof session.action_layer === "object"
      ? session.action_layer
      : {};
    const actionLines = [
      `overall=${String(action.overall_status || "UNKNOWN")}`,
      `components=${JSON.stringify(action.component_status || {})}`,
      `status_counts=${JSON.stringify(action.action_log_status_counts || {})}`,
      `result_states=${JSON.stringify(action.action_log_result_state_counts || {})}`,
    ];
    renderSessionLines("session-action-list", actionLines);

    const warnings = Array.isArray(session.warnings) ? session.warnings : [];
    renderSessionLines("session-warnings-list", warnings);

    const timelineNode = document.getElementById("session-timeline-list");
    timelineNode.innerHTML = "";
    const timeline = session.timeline && Array.isArray(session.timeline.events)
      ? session.timeline.events
      : [];
    const recent = timeline.slice(Math.max(0, timeline.length - 18));
    if (recent.length === 0) {
      const placeholder = document.createElement("p");
      placeholder.className = "placeholder";
      placeholder.textContent = t.sessionNoData;
      timelineNode.appendChild(placeholder);
    } else {
      recent.forEach((event) => {
        const card = document.createElement("article");
        card.className = "session-event";
        card.innerHTML = `
          <div class="session-event__top">
            <span>${String(event.timestamp_utc || "-")}</span>
            <span class="status-pill ${statusClass(event.status)}">${String(event.status || "UNKNOWN")}</span>
          </div>
          <p>${String(event.run_kind || "RUN")} :: ${String(event.summary || "")}</p>
          <p class="session-event__meta">${String(event.source_path || "-")}</p>
        `;
        timelineNode.appendChild(card);
      });
    }
  }

  function ownerGateStatusClass(derivedStatus) {
    const value = String(derivedStatus || "");
    if (value.includes("BLOCKING")) {
      return "status-block";
    }
    if (value.includes("WARN")) {
      return "status-warn";
    }
    return "status-foundation";
  }

  function blockingLevelStatusClass(level) {
    const value = String(level || "");
    if (value === "BLOCKING") {
      return "status-block";
    }
    if (value === "WARN_ONLY") {
      return "status-warn";
    }
    return "status-foundation";
  }

  function pickQuestionText(question) {
    if (state.lang === "ru") {
      return String(question.question_text_ru || "-");
    }
    return String(question.question_text_en_optional || question.question_text_ru || "-");
  }

  function renderOwnerQuestionGate() {
    const t = I18N[state.lang];
    const gate = state.ownerQuestionGate;

    if (!gate || typeof gate !== "object") {
      const pill = document.getElementById("owner-gate-pill");
      pill.textContent = "NOT_READY";
      pill.className = "status-pill status-not-ready";
      setText("owner-total", "-");
      setText("owner-open", "-");
      setText("owner-blocking", "-");
      setText("owner-deferred", "-");
      setText("owner-warn-only", "-");
      setText("owner-required", "-");
      setText("owner-derived-status", "NOT_READY");
      setText("owner-next-step", "-");
      setText("owner-boundary-note", t.ownerQuestionBoundary);
      renderSessionLines("owner-question-warnings-list", [t.ownerQuestionNoData]);
      const cardsNode = document.getElementById("owner-question-cards");
      cardsNode.innerHTML = `<p class=\"placeholder\">${t.ownerQuestionNoData}</p>`;
      return;
    }

    const summary = gate.summary && typeof gate.summary === "object" ? gate.summary : {};
    const derivedStatus = String(summary.derived_gate_status || "FOUNDATION_SAMPLE_ONLY");
    const pill = document.getElementById("owner-gate-pill");
    pill.textContent = derivedStatus;
    pill.className = `status-pill ${ownerGateStatusClass(derivedStatus)}`;

    setText("owner-total", String(summary.total_questions ?? 0));
    setText("owner-open", String(summary.open_count ?? 0));
    setText("owner-blocking", String(summary.blocking_count ?? 0));
    setText("owner-deferred", String(summary.deferred_count ?? 0));
    setText("owner-warn-only", String(summary.warn_only_count ?? 0));
    setText("owner-required", String(summary.owner_answer_required_count ?? 0));
    setText("owner-derived-status", derivedStatus);
    setText("owner-next-step", String(gate.next_required_step || "-"));
    setText("owner-boundary-note", String(gate.boundary_note || t.ownerQuestionBoundary));

    const warnings = Array.isArray(gate.warnings) ? gate.warnings : [];
    renderSessionLines("owner-question-warnings-list", warnings.length > 0 ? warnings : ["-"]);

    const cardsNode = document.getElementById("owner-question-cards");
    cardsNode.innerHTML = "";
    const questions = Array.isArray(gate.questions) ? gate.questions : [];
    if (questions.length === 0) {
      cardsNode.innerHTML = `<p class=\"placeholder\">${t.ownerQuestionNoData}</p>`;
      return;
    }

    questions.slice(0, 8).forEach((question) => {
      const evidenceRefs = Array.isArray(question.evidence_refs) ? question.evidence_refs : [];
      const card = document.createElement("article");
      card.className = "owner-question-card";
      card.innerHTML = `
        <div class="owner-question-card__top">
          <strong>${String(question.question_id || "-")}</strong>
          <span class="status-pill ${statusClass(question.status)}">${String(question.status || "UNKNOWN")}</span>
        </div>
        <div class="owner-question-card__meta">
          <span class="status-pill ${blockingLevelStatusClass(question.blocking_level)}">${String(question.blocking_level || "-")}</span>
          <span>${String(question.source || "-")} :: ${String(question.decision_type || "-")}</span>
        </div>
        <p class="owner-question-card__question">${pickQuestionText(question)}</p>
        <p class="owner-question-card__why">${String(question.why_needed_ru || "-")}</p>
        <p class="owner-question-card__meta">${t.ownerQuestionNotWired}</p>
        <ul class="owner-question-card__evidence"></ul>
      `;
      const evidenceNode = card.querySelector(".owner-question-card__evidence");
      if (evidenceRefs.length === 0) {
        const li = document.createElement("li");
        li.textContent = "-";
        evidenceNode.appendChild(li);
      } else {
        evidenceRefs.slice(0, 3).forEach((item) => {
          const li = document.createElement("li");
          li.textContent = String(item);
          evidenceNode.appendChild(li);
        });
      }
      cardsNode.appendChild(card);
    });
  }

  function renderTransferConsole() {
    const t = I18N[state.lang];
    const view = state.transferConsoleView;
    const pill = document.getElementById("transfer-pill");
    const cardNode = document.getElementById("transfer-contour-cards");

    if (!view || typeof view !== "object") {
      pill.textContent = "NOT_READY";
      pill.className = "status-pill status-not-ready";
      setText("transfer-generated", "-");
      setText("transfer-boundary", "FOUNDATION_ONLY");
      setText("transfer-request-count", "-");
      setText("transfer-result-count", "-");
      setText("transfer-ledger-count", "-");
      setText("transfer-context-mix", "-");
      setText("transfer-runner-state", "NOT_READY");
      setText("transfer-shell-safety", "UNKNOWN");
      cardNode.innerHTML = `<p class=\"placeholder\">${t.transferNoData}</p>`;
      renderSessionLines("transfer-request-list", [t.transferNoData]);
      renderSessionLines("transfer-result-list", [t.transferNoData]);
      renderSessionLines("transfer-ledger-list", [t.transferNoData]);
      renderSessionLines("transfer-source-refs", ["-"]);
      setText("transfer-runner-note", t.transferRunnerNote);
      setText("transfer-boundary-note", t.transferBoundaryNote);
      return;
    }

    const boundary = String(view.claim_boundary || "FOUNDATION_ONLY");
    pill.textContent = boundary;
    pill.className = `status-pill ${statusClass(boundary)}`;

    const requests = Array.isArray(view.latest_requests) ? view.latest_requests : [];
    const results = Array.isArray(view.latest_results) ? view.latest_results : [];
    const ledger = Array.isArray(view.action_ledger) ? view.action_ledger : [];
    const contours = Array.isArray(view.contour_cards) ? view.contour_cards : [];
    const sourceRefs = Array.isArray(view.source_refs) ? view.source_refs : [];
    const runnerState = view.action_runner_state && typeof view.action_runner_state === "object"
      ? view.action_runner_state
      : null;
    const runnerRequests = runnerState && Array.isArray(runnerState.latest_action_requests)
      ? runnerState.latest_action_requests
      : [];
    const runnerResults = runnerState && Array.isArray(runnerState.latest_action_results)
      ? runnerState.latest_action_results
      : [];
    const runnerLedger = runnerState && Array.isArray(runnerState.latest_runner_ledger)
      ? runnerState.latest_runner_ledger
      : [];
    const mix = view.context_source_mix && typeof view.context_source_mix === "object"
      ? view.context_source_mix
      : {};

    const requestRows = runnerRequests.length > 0 ? runnerRequests : requests;
    const resultRows = runnerResults.length > 0 ? runnerResults : results;
    const ledgerRows = runnerLedger.length > 0 ? runnerLedger : ledger;
    const requestById = new Map(
      requestRows
        .filter((item) => item && typeof item === "object")
        .map((item) => [String(item.request_id || ""), item])
    );
    const runnerLastAction = runnerState && runnerState.last_action && typeof runnerState.last_action === "object"
      ? runnerState.last_action
      : null;
    const shellSafe = runnerState ? Boolean(runnerState.no_arbitrary_shell_confirmed) : false;
    const runnerStateText = runnerState
      ? String(runnerLastAction && runnerLastAction.action_id ? runnerLastAction.action_id : "READY")
      : "NOT_READY";

    setText("transfer-generated", String(view.generated_at_utc || "-"));
    setText("transfer-boundary", boundary);
    setText("transfer-request-count", String(requestRows.length));
    setText("transfer-result-count", String(resultRows.length));
    setText("transfer-ledger-count", String(ledgerRows.length));
    setText(
      "transfer-context-mix",
      `T${String(mix.taskpack_percent ?? "-")} R${String(mix.existing_newgen_repo_percent ?? "-")} O${String(mix.owner_handoff_percent ?? "-")}`
    );
    setText("transfer-runner-state", runnerStateText);
    setText("transfer-shell-safety", shellSafe ? "CONFIRMED" : "UNKNOWN");
    if (runnerState) {
      const limitations = Array.isArray(runnerState.known_limitations) ? runnerState.known_limitations : [];
      const lastRef = runnerLastAction ? String(runnerLastAction.result_ref || "-") : "-";
      const routeProofStatus = runnerLastAction ? String(runnerLastAction.route_proof_status || "-") : "-";
      const routeProofRoute = runnerLastAction ? String(runnerLastAction.route || "-") : "-";
      const routeProofVerdict = runnerLastAction ? String(runnerLastAction.route_proof_verdict || "-") : "-";
      const runnerNote = `${runnerStateText} :: route=${routeProofRoute} :: ${routeProofStatus} :: verdict=${routeProofVerdict} :: result_ref=${lastRef} :: ${String(limitations[0] || "FOUNDATION_ONLY")}`;
      setText("transfer-runner-note", runnerNote);
    } else {
      setText("transfer-runner-note", t.transferRunnerNote);
    }
    setText("transfer-boundary-note", t.transferBoundaryNote);

    cardNode.innerHTML = "";
    if (contours.length === 0) {
      cardNode.innerHTML = `<p class=\"placeholder\">${t.transferNoData}</p>`;
    } else {
      contours.forEach((contour) => {
        const card = document.createElement("article");
        card.className = "transfer-contour-card";
        card.innerHTML = `
          <div class="transfer-contour-card__top">
            <strong>${String(contour.contour_id || contour.display_name || "-")}</strong>
            <span class="status-pill ${statusClass(contour.status)}">${String(contour.status || "UNKNOWN")}</span>
          </div>
          <p>${String(contour.status_reason || "-")}</p>
          <p class="transfer-contour-card__meta">route: ${String(contour.route_config_status || "-")}</p>
          <p class="transfer-contour-card__meta">probe: ${String(contour.last_probe_receipt_ref || "N/A")}</p>
        `;
        cardNode.appendChild(card);
      });
    }

    const requestLines = requestRows.slice(0, 8).map((item) => {
      const source = String(item.source_contour || "?");
      const target = String(item.target_contour || "?");
      const route = `${source}->${target}`;
      return `${String(item.request_id || "-")} :: ${String(item.action_type || "-")} :: route=${route} :: mode=${String(item.mode || "N/A")} :: ${String(item.status || "-")}`;
    });
    const resultLines = resultRows.slice(0, 8).map((item) => {
      const requestRef = requestById.get(String(item.request_id || ""));
      const source = requestRef ? String(requestRef.source_contour || "?") : "?";
      const target = requestRef ? String(requestRef.target_contour || "?") : "?";
      const route = `${source}->${target}`;
      const limitations = Array.isArray(item.limitations) ? item.limitations : [];
      return `${String(item.result_id || "-")} :: ${String(item.action_type || "-")} :: route=${route} :: ${String(item.status || "-")} :: evidence=${String((Array.isArray(item.evidence_refs) ? item.evidence_refs.length : 0))} :: ${String(limitations[0] || "-")}`;
    });
    const ledgerLines = ledgerRows.slice(-10).map((item) =>
      `${String(item.timestamp_utc || "-")} :: ${String(item.action_type || item.action_id || "-")} :: ${String(item.status || item.result_status || "-")}`
    );

    renderSessionLines("transfer-request-list", requestLines.length > 0 ? requestLines : ["-"]);
    renderSessionLines("transfer-result-list", resultLines.length > 0 ? resultLines : ["-"]);
    renderSessionLines("transfer-ledger-list", ledgerLines.length > 0 ? ledgerLines : ["-"]);
    renderSessionLines("transfer-source-refs", sourceRefs.length > 0 ? sourceRefs : ["-"]);
  }

  function renderInspector() {
    const phase = state.data.phases.find((item) => item.phase_no === state.selectedPhaseNo);
    const empty = document.getElementById("inspector-empty");
    const body = document.getElementById("inspector-body");

    if (!phase) {
      empty.classList.remove("hidden");
      body.classList.add("hidden");
      return;
    }

    empty.classList.add("hidden");
    body.classList.remove("hidden");

    setText("inspector-phase-name", `${phase.phase_no}. ${phase.name} [${phase.status}]`);
    setText("inspector-summary", phase.summary || "");

    renderList("inspector-paths", phase.paths || []);
    renderList("inspector-reports", phase.report_paths || []);
    renderList("inspector-limits", phase.limitations || []);

    const jsonBox = document.getElementById("inspector-json");
    jsonBox.textContent = JSON.stringify(phase, null, 2);
  }

  function renderList(id, items) {
    const node = document.getElementById(id);
    node.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
      const li = document.createElement("li");
      li.textContent = "-";
      node.appendChild(li);
      return;
    }

    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = String(item);
      node.appendChild(li);
    });
  }

  function renderConnection() {
    const t = I18N[state.lang];
    const pill = document.getElementById("connection-status-pill");

    let label = t.serverUnknown;
    let note = state.connectionNote || "";

    if (state.serverStatus === "CONNECTED") {
      label = t.serverConnected;
      if (!note) {
        note = t.serverConnectedNote;
      }
    } else if (state.serverStatus === "NOT_CONNECTED") {
      label = t.serverNotConnected;
      if (!note) {
        note = t.serverNotConnectedRuntime;
      }
    }

    pill.className = `status-pill ${statusClass(label)}`;
    pill.textContent = label;
    setText("connection-note", note || t.serverUnknown);
  }

  function safeActionStatus(result) {
    if (!result || typeof result !== "object") {
      return I18N[state.lang].statusUnknown;
    }

    const status = String(result.status || I18N[state.lang].statusUnknown);
    const evidence = Array.isArray(result.evidence_refs) ? result.evidence_refs : [];

    if (status === "PASS" && evidence.length === 0) {
      return "WARN";
    }
    return status;
  }

  function renderLastActionResult() {
    const t = I18N[state.lang];
    const result = state.lastActionResult;

    setStatusValue("registry-status", state.registryStatus || "UNKNOWN");
    setStatusValue("report-summary-status", state.reportSummaryState || "UNKNOWN");
    setStatusValue("result-model-state", state.lastActionModelState || "ACTION_RESULT_WARN");

    if (!result || typeof result !== "object") {
      setStatusValue("last-action-status", "UNKNOWN");
      setText("last-action-path", "-");
      setText("last-action-summary", t.noResult);
      setText("last-action-json", "-");
      return;
    }

    const safeStatus = safeActionStatus(result);
    const evidence = Array.isArray(result.evidence_refs) ? result.evidence_refs : [];
    const downgrade = String(result.status) === "PASS" && evidence.length === 0;

    setStatusValue("last-action-status", safeStatus);
    setText("last-action-path", String(result.result_record_path || "-"));
    setText(
      "last-action-summary",
      downgrade ? `${String(result.output_summary || "")}; ${t.noEvidenceDowngrade}` : String(result.output_summary || "-")
    );
    setText("last-action-json", JSON.stringify(result, null, 2));
  }

  function renderActionCards() {
    const t = I18N[state.lang];
    const container = document.getElementById("action-cards");
    container.innerHTML = "";

    state.actions.forEach((action) => {
      const card = document.createElement("article");
      card.className = "action-card";

      const runEnabled =
        state.serverStatus === "CONNECTED" &&
        action.status === "WIRED" &&
        action.availability_state === "ACTION_ALLOWED";
      let buttonLabel = t.unavailable;
      if (action.status === "PREVIEW_ONLY") {
        buttonLabel = t.previewOnly;
      } else if (runEnabled) {
        buttonLabel = t.runAction;
      }

      const limits = Array.isArray(action.known_limitations) ? action.known_limitations : [];
      const evidence = Array.isArray(action.evidence_refs) ? action.evidence_refs : [];

      card.innerHTML = `
        <div class="action-card__top">
          <h3>${action.title}</h3>
          <span class="status-pill ${statusClass(action.status)}">${action.status}</span>
        </div>
        <p class="action-id">${action.action_id}</p>
        <p class="action-desc">${action.description}</p>
        <p class="action-safety">${action.availability_state}</p>
        <p class="action-safety">${action.safety_level}</p>
        <p class="action-evidence">evidence refs: ${evidence.length}</p>
        <ul class="action-limits"></ul>
      `;

      const limitsNode = card.querySelector(".action-limits");
      if (limits.length === 0) {
        const li = document.createElement("li");
        li.textContent = "-";
        limitsNode.appendChild(li);
      } else {
        limits.slice(0, 3).forEach((item) => {
          const li = document.createElement("li");
          li.textContent = String(item);
          limitsNode.appendChild(li);
        });
      }

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn action-run";
      btn.textContent = buttonLabel;
      btn.disabled = !runEnabled;

      btn.addEventListener("click", async function () {
        await runAction(action.action_id);
      });

      card.appendChild(btn);
      container.appendChild(card);
    });
  }

  async function runAction(actionId) {
    const t = I18N[state.lang];
    if (state.serverStatus !== "CONNECTED") {
      state.connectionNote = t.serverNotConnectedRuntime;
      renderConnection();
      return;
    }

    state.lastActionResult = {
      status: t.running,
      result_record_path: "-",
      output_summary: `${actionId}: ${t.running}`,
      evidence_refs: []
    };
    renderLastActionResult();

    try {
      const response = await fetch(`/api/actions/${encodeURIComponent(actionId)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          requester: "SANCTUM_NG_UI",
          dry_run: false,
          input: {
            origin: "UI"
          }
        })
      });

      const payload = await response.json();
      applyLatestActionResult(payload && typeof payload === "object" ? payload : {
        status: "ERROR",
        result_record_path: "-",
        output_summary: "Invalid action response payload.",
        evidence_refs: [],
        state_model: {
          result_state: "ACTION_RESULT_BLOCK"
        }
      });
    } catch (error) {
      applyLatestActionResult({
        status: "ERROR",
        result_record_path: "-",
        output_summary: `ACTION_REQUEST_ERROR: ${String(error)}`,
        evidence_refs: [],
        state_model: {
          result_state: "ACTION_RESULT_BLOCK"
        }
      });
    }

    renderLastActionResult();
  }

  function renderAll() {
    setLabels();
    renderTruthBar();
    renderRail();
    renderCommunicationGate();
    renderTruthIndex();
    renderOrganDialogueDemo();
    renderServitorSessionView();
    renderOwnerQuestionGate();
    renderTransferConsole();
    renderPipeline();
    renderInspector();
    renderConnection();
    renderActionCards();
    renderLastActionResult();
  }

  async function bootstrapData() {
    const t = I18N[state.lang];

    if (window.location.protocol === "file:") {
      state.serverStatus = "NOT_CONNECTED";
      state.connectionNote = t.serverNotConnectedFile;
      state.data = normalizeData({ ...FALLBACK_STATE });
      state.data.warnings.push("ACTION_SERVER_NOT_CONNECTED");
      state.actions = normalizeActions(FALLBACK_ACTIONS);
      state.sessionView = null;
      state.ownerQuestionGate = normalizeOwnerQuestionGate(FALLBACK_OWNER_QUESTION_GATE);
      state.transferConsoleView = normalizeTransferConsole(FALLBACK_TRANSFER_CONSOLE_VIEW);
      state.registryStatus = "ACTION_DISABLED";
      state.reportSummaryState = "NOT_READY";
      state.reportSummaryReason = "file_mode_no_server";
      state.lastActionModelState = "ACTION_RESULT_WARN";
      return;
    }

    try {
      const stateRes = await fetch("/api/state", { cache: "no-store" });
      const actionsRes = await fetch("/api/actions", { cache: "no-store" });

      if (!stateRes.ok || !actionsRes.ok) {
        throw new Error(`api_status:${stateRes.status}/${actionsRes.status}`);
      }

      const statePayload = await stateRes.json();
      const actionsPayload = await actionsRes.json();

      state.data = normalizeData(statePayload && typeof statePayload === "object" ? statePayload.state : null);
      state.actions = normalizeActions(actionsPayload && typeof actionsPayload === "object" ? actionsPayload.actions : null);
      state.serverStatus = String((statePayload || {}).status || "CONNECTED");
      state.connectionNote = t.serverConnectedNote;
      state.registryStatus = String((((actionsPayload || {}).registry) || {}).status || "UNKNOWN");
      state.actionLayerStateModel = (statePayload || {}).action_layer_state_model || (actionsPayload || {}).action_layer_state_model || null;
      state.sessionView = (statePayload || {}).servitor_session_view || (state.data || {}).servitor_session_view || null;
      state.ownerQuestionGate = normalizeOwnerQuestionGate(
        (statePayload || {}).owner_question_gate || (state.data || {}).owner_question_gate || null
      );
      state.transferConsoleView = normalizeTransferConsole(
        (statePayload || {}).transfer_console_view || (state.data || {}).transfer_console_view || null
      );

      applyReportSummary((statePayload || {}).latest_report_summary || null);
      applyLatestActionResult((statePayload || {}).latest_action_result || null);
    } catch (error) {
      state.data = normalizeData({ ...FALLBACK_STATE });
      state.actions = normalizeActions(FALLBACK_ACTIONS);
      state.sessionView = null;
      state.ownerQuestionGate = normalizeOwnerQuestionGate(FALLBACK_OWNER_QUESTION_GATE);
      state.transferConsoleView = normalizeTransferConsole(FALLBACK_TRANSFER_CONSOLE_VIEW);
      state.serverStatus = "NOT_CONNECTED";
      state.connectionNote = `${t.serverNotConnectedRuntime}; ${String(error)}`;
      state.data.warnings.push(`ACTION_LAYER_API_LOAD_ERROR:${String(error)}`);
      state.registryStatus = "ACTION_DISABLED";
      state.reportSummaryState = "NOT_READY";
      state.reportSummaryReason = "api_unreachable";
      state.lastActionModelState = "ACTION_RESULT_WARN";
    }
  }

  async function bootstrap() {
    const langBtn = document.getElementById("lang-toggle");
    langBtn.addEventListener("click", function () {
      state.lang = state.lang === "en" ? "ru" : "en";
      renderAll();
    });

    await bootstrapData();

    if (!state.selectedPhaseNo) {
      state.selectedPhaseNo = 1;
    }

    renderAll();
  }

  bootstrap();
})();
