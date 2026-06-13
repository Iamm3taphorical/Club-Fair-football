export type DNAStats = {
  creativity: number;
  finishing: number;
  vision: number;
  speed: number;
  leadership: number;
  flair: number;
};

export type DNATraits = {
  Vision: number;
  Creativity: number;
  Power: number;
  Speed: number;
};

export type DNAProfile = {
  primary_match: string;
  name_match?: string;
  display_name?: string;
  style?: string;
  archetype?: string;
  traits?: DNATraits;
  stats: DNAStats;
  percentages: Record<string, number>;
  special_ability?: string;
  suggested_role?: string;
  strength?: string;
  weakness?: string;
  confidence_score?: number;
  confidence_status?: string;
  identity_basis?: string;
  scan?: {
    status?: string;
    face_detected?: boolean;
    dataset_url?: string;
    dataset_path?: string;
    dataset_present?: boolean;
    index_path?: string;
    index_present?: boolean;
    embedding_model?: string;
    confidence_threshold?: number;
    matching_method?: string;
    fallback_reason?: string;
    identity_basis?: string;
  };
};

export type UserProfile = {
  user_id: string;
  id?: string;
  name: string;
  timestamp?: string;
  last_login_at?: string;
  session_history?: unknown[];
  dna?: DNAProfile | Record<string, never>;
};

export type PenaltyAttempt = {
  id?: number;
  gesture: string;
  shot_type: string;
  shot_target: string;
  result: 'Goal' | 'Saved' | 'Missed';
  keeper_guess: string;
  reaction_time: number;
  power: number;
  curve: number;
  commentary: string;
  timestamp?: string;
};

export type PenaltySessionSnapshot = {
  session_id: number;
  match_session_id?: number;
  player_id: string;
  challenge: string;
  status: 'active' | 'completed';
  started_at: string;
  completed_at?: string | null;
  goals: number;
  accuracy: number;
  average_reaction_time: number;
  dna_after?: DNAProfile | Record<string, never>;
  attempts: PenaltyAttempt[];
};

export type PlayerReport = {
  player_type: string;
  goals: number;
  total_shots: number;
  score: string;
  accuracy: number;
  reaction_time: number;
  best_skill: string;
  weakness: string;
  suggested_role: string;
  dna_before: DNAProfile;
  dna_after: DNAProfile;
  evolution: string;
  radar_chart: Array<{ label: string; value: number }>;
  performance_graph: Array<{ shot: number; goals: number; result: string }>;
  shareable_card: { title: string; headline: string; rating: number };
  match_story: string;
};

export type CoachScenario = {
  segment: string;
  current_score: string;
  opponent_formation: string;
  opponent_strategy: string;
  objective: string;
  pressure_level: string;
  coach_style?: string;
};

export type CoachTactics = {
  coach_style: string;
  formation: string;
  attack: number;
  defense: number;
  possession: number;
  pressure: number;
  width: number;
  roles: Record<string, string>;
  player_positions: Array<{ id: number; label: string; x: number; y: number }>;
};

export interface CoachResult {
  final_score: string;
  timeline: string[];
  total_points: number;
  session_id?: number;
  manager_title?: string;
}
